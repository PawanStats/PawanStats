from __future__ import annotations

import argparse
import csv
import json
import math
import os
from dataclasses import asdict, dataclass
from datetime import date, datetime, time, timedelta
from pathlib import Path
from typing import Any, Dict, Iterable, List, Optional, Protocol, Sequence, Tuple
from urllib import error, parse, request


ENTRY_TIME = time(9, 17)
EXIT_TIME = time(15, 10)
STRIKE_STEP = 50
STOPLOSS_PCT = 0.25
UNDERLYING = "NIFTY"


@dataclass(frozen=True)
class Candle:
    timestamp: datetime
    close: float


@dataclass(frozen=True)
class TradeResult:
    trade_date: date
    expiry: date
    strike: int
    entry_time: datetime
    exit_time: datetime
    exit_reason: str
    ce_entry: float
    pe_entry: float
    ce_exit: float
    pe_exit: float
    entry_combined: float
    exit_combined: float
    pnl: float


@dataclass
class DhanAPIConfig:
    base_url: str = "https://api.dhan.co"
    spot_historical_path: str = "/v2/charts/historical"
    option_historical_path: str = "/v2/charts/historical/options"
    option_chain_path: str = "/v2/options/chain"


class HistoricalDataAdapter(Protocol):
    def get_spot_candles(self, trading_date: date) -> List[Candle]: ...

    def get_option_candles(
        self,
        trading_date: date,
        expiry: date,
        strike: int,
        option_type: str,
    ) -> List[Candle]: ...

    def get_weekly_expiries(self, as_of_date: date) -> List[date]: ...


class DhanHistoricalAdapter:
    """
    Dhan API adapter.

    Endpoint paths and payload keys can vary between Dhan API versions/accounts.
    Update DhanAPIConfig values and payload field names here if needed.
    """

    def __init__(
        self,
        client_id: str,
        access_token: str,
        config: Optional[DhanAPIConfig] = None,
        timeout_seconds: int = 30,
    ) -> None:
        self.client_id = client_id
        self.access_token = access_token
        self.config = config or DhanAPIConfig()
        self.timeout_seconds = timeout_seconds

    def _headers(self) -> Dict[str, str]:
        return {
            "Content-Type": "application/json",
            "client-id": self.client_id,
            "access-token": self.access_token,
        }

    def _request_json(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = json.dumps(payload).encode("utf-8")
        req = request.Request(
            url=f"{self.config.base_url}{path}",
            data=body,
            headers=self._headers(),
            method="POST",
        )
        try:
            with request.urlopen(req, timeout=self.timeout_seconds) as response:
                return json.loads(response.read().decode("utf-8"))
        except error.HTTPError as exc:
            details = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(f"Dhan API HTTP error {exc.code}: {details}") from exc
        except error.URLError as exc:
            raise RuntimeError(f"Dhan API network error: {exc.reason}") from exc

    @staticmethod
    def _parse_timestamp(raw: Any) -> datetime:
        if isinstance(raw, (int, float)):
            value = float(raw)
            if value > 1e12:
                value /= 1000.0
            return datetime.fromtimestamp(value)
        if isinstance(raw, str):
            text = raw.strip().replace("Z", "+00:00")
            try:
                return datetime.fromisoformat(text)
            except ValueError:
                return datetime.strptime(raw, "%Y-%m-%d %H:%M:%S")
        raise ValueError(f"Unsupported timestamp format: {raw!r}")

    @classmethod
    def _parse_candles(cls, payload: Dict[str, Any]) -> List[Candle]:
        rows = payload.get("data") or payload.get("candles") or []
        candles: List[Candle] = []
        for row in rows:
            if isinstance(row, dict):
                ts = row.get("timestamp") or row.get("time") or row.get("datetime")
                close = row.get("close") or row.get("c")
            elif isinstance(row, (list, tuple)) and len(row) >= 5:
                ts, close = row[0], row[4]
            else:
                continue
            if ts is None or close is None:
                continue
            candles.append(Candle(timestamp=cls._parse_timestamp(ts), close=float(close)))
        candles.sort(key=lambda c: c.timestamp)
        return candles

    def get_spot_candles(self, trading_date: date) -> List[Candle]:
        payload = {
            "symbol": UNDERLYING,
            "exchangeSegment": "IDX_I",
            "interval": "1",
            "fromDate": trading_date.isoformat(),
            "toDate": trading_date.isoformat(),
        }
        response = self._request_json(self.config.spot_historical_path, payload)
        return self._parse_candles(response)

    def get_option_candles(
        self,
        trading_date: date,
        expiry: date,
        strike: int,
        option_type: str,
    ) -> List[Candle]:
        payload = {
            "symbol": UNDERLYING,
            "exchangeSegment": "NSE_FNO",
            "instrument": "OPTIDX",
            "interval": "1",
            "expiryDate": expiry.isoformat(),
            "strikePrice": strike,
            "optionType": option_type,
            "fromDate": trading_date.isoformat(),
            "toDate": trading_date.isoformat(),
        }
        response = self._request_json(self.config.option_historical_path, payload)
        return self._parse_candles(response)

    def get_weekly_expiries(self, as_of_date: date) -> List[date]:
        payload = {
            "underlying": UNDERLYING,
            "exchangeSegment": "NSE_FNO",
            "asOfDate": as_of_date.isoformat(),
        }
        response = self._request_json(self.config.option_chain_path, payload)
        raw = response.get("expiries") or response.get("expiryDates") or []
        parsed: List[date] = []
        for item in raw:
            if isinstance(item, str):
                parsed.append(datetime.strptime(item[:10], "%Y-%m-%d").date())
        return sorted(set(parsed))


def get_required_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise EnvironmentError(f"Missing environment variable: {name}")
    return value


def daterange(start: date, end: date) -> Iterable[date]:
    current = start
    while current <= end:
        yield current
        current += timedelta(days=1)


def nearest_weekly_expiry(as_of_date: date, expiries: Optional[Sequence[date]] = None) -> date:
    if expiries:
        upcoming = sorted(expiry for expiry in expiries if expiry >= as_of_date)
        if upcoming:
            return upcoming[0]
    days_to_thursday = (3 - as_of_date.weekday()) % 7
    return as_of_date + timedelta(days=days_to_thursday)


def select_atm_strike(spot_price: float, step: int = STRIKE_STEP) -> int:
    return int(step * math.floor((spot_price / step) + 0.5))


def first_candle_at_or_after(candles: Sequence[Candle], target_time: time) -> Optional[Candle]:
    for candle in candles:
        if candle.timestamp.time() >= target_time:
            return candle
    return None


def _build_price_map(candles: Sequence[Candle]) -> Dict[datetime, float]:
    return {candle.timestamp: candle.close for candle in candles}


def simulate_intraday_exit(
    ce_candles: Sequence[Candle],
    pe_candles: Sequence[Candle],
    stoploss_pct: float = STOPLOSS_PCT,
    entry_time: time = ENTRY_TIME,
    exit_time: time = EXIT_TIME,
) -> Tuple[datetime, float, float, str, float, float]:
    ce_entry = first_candle_at_or_after(ce_candles, entry_time)
    pe_entry = first_candle_at_or_after(pe_candles, entry_time)
    if not ce_entry or not pe_entry:
        raise ValueError("Missing CE/PE entry candle at or after entry time")

    entry_ts = max(ce_entry.timestamp, pe_entry.timestamp)
    entry_combined = ce_entry.close + pe_entry.close
    stoploss_level = entry_combined * (1.0 + stoploss_pct)
    exit_limit = datetime.combine(entry_ts.date(), exit_time)

    ce_map = _build_price_map(ce_candles)
    pe_map = _build_price_map(pe_candles)
    all_times = sorted(ts for ts in set(ce_map) | set(pe_map) if entry_ts <= ts <= exit_limit)

    current_ce = ce_entry.close
    current_pe = pe_entry.close
    for ts in all_times:
        if ts in ce_map:
            current_ce = ce_map[ts]
        if ts in pe_map:
            current_pe = pe_map[ts]
        if current_ce + current_pe >= stoploss_level:
            return ts, current_ce, current_pe, "stoploss", ce_entry.close, pe_entry.close

    ce_exit = first_candle_at_or_after(ce_candles, exit_time)
    pe_exit = first_candle_at_or_after(pe_candles, exit_time)

    if ce_exit and pe_exit:
        return (
            max(ce_exit.timestamp, pe_exit.timestamp),
            ce_exit.close,
            pe_exit.close,
            "time_exit",
            ce_entry.close,
            pe_entry.close,
        )

    fallback_ts = all_times[-1] if all_times else entry_ts
    return fallback_ts, current_ce, current_pe, "time_exit", ce_entry.close, pe_entry.close


def run_backtest(
    adapter: HistoricalDataAdapter,
    start_date: date,
    end_date: date,
    stoploss_pct: float = STOPLOSS_PCT,
) -> List[TradeResult]:
    trades: List[TradeResult] = []

    for trading_date in daterange(start_date, end_date):
        if trading_date.weekday() >= 5:
            continue

        try:
            spot_candles = adapter.get_spot_candles(trading_date)
            spot_entry = first_candle_at_or_after(spot_candles, ENTRY_TIME)
            if not spot_entry:
                continue

            strike = select_atm_strike(spot_entry.close)
            expiries = adapter.get_weekly_expiries(trading_date)
            expiry = nearest_weekly_expiry(trading_date, expiries)

            ce_candles = adapter.get_option_candles(trading_date, expiry, strike, "CE")
            pe_candles = adapter.get_option_candles(trading_date, expiry, strike, "PE")
            if not ce_candles or not pe_candles:
                continue

            (
                exit_ts,
                ce_exit,
                pe_exit,
                exit_reason,
                ce_entry,
                pe_entry,
            ) = simulate_intraday_exit(
                ce_candles=ce_candles,
                pe_candles=pe_candles,
                stoploss_pct=stoploss_pct,
            )

            entry_combined = ce_entry + pe_entry
            exit_combined = ce_exit + pe_exit
            pnl = (ce_entry - ce_exit) + (pe_entry - pe_exit)

            trades.append(
                TradeResult(
                    trade_date=trading_date,
                    expiry=expiry,
                    strike=strike,
                    entry_time=datetime.combine(trading_date, ENTRY_TIME),
                    exit_time=exit_ts,
                    exit_reason=exit_reason,
                    ce_entry=ce_entry,
                    pe_entry=pe_entry,
                    ce_exit=ce_exit,
                    pe_exit=pe_exit,
                    entry_combined=entry_combined,
                    exit_combined=exit_combined,
                    pnl=pnl,
                )
            )
        except Exception as exc:
            print(f"Skipping {trading_date}: {exc}")

    return trades


def summarize_trades(trades: Sequence[TradeResult]) -> Dict[str, Any]:
    if not trades:
        return {
            "trades": 0,
            "total_pnl": 0.0,
            "avg_pnl": 0.0,
            "win_rate": 0.0,
            "max_drawdown": 0.0,
            "stoploss_exits": 0,
            "time_exits": 0,
        }

    pnls = [trade.pnl for trade in trades]
    total_pnl = sum(pnls)
    avg_pnl = total_pnl / len(pnls)
    wins = sum(1 for pnl in pnls if pnl > 0)
    win_rate = wins / len(pnls)

    running = 0.0
    peak = 0.0
    max_drawdown = 0.0
    for pnl in pnls:
        running += pnl
        peak = max(peak, running)
        max_drawdown = max(max_drawdown, peak - running)

    return {
        "trades": len(trades),
        "total_pnl": round(total_pnl, 2),
        "avg_pnl": round(avg_pnl, 2),
        "win_rate": round(win_rate, 4),
        "max_drawdown": round(max_drawdown, 2),
        "stoploss_exits": sum(1 for trade in trades if trade.exit_reason == "stoploss"),
        "time_exits": sum(1 for trade in trades if trade.exit_reason == "time_exit"),
    }


def export_results(trades: Sequence[TradeResult], output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)

    trades_path = output_dir / "nifty_short_straddle_trades.csv"
    summary_path = output_dir / "nifty_short_straddle_summary.json"

    with trades_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=list(asdict(trades[0]).keys()) if trades else [
                "trade_date",
                "expiry",
                "strike",
                "entry_time",
                "exit_time",
                "exit_reason",
                "ce_entry",
                "pe_entry",
                "ce_exit",
                "pe_exit",
                "entry_combined",
                "exit_combined",
                "pnl",
            ],
        )
        writer.writeheader()
        for trade in trades:
            row = asdict(trade)
            row["trade_date"] = row["trade_date"].isoformat()
            row["expiry"] = row["expiry"].isoformat()
            row["entry_time"] = row["entry_time"].isoformat(sep=" ")
            row["exit_time"] = row["exit_time"].isoformat(sep=" ")
            writer.writerow(row)

    summary = summarize_trades(trades)
    with summary_path.open("w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    print(f"Trades exported to: {trades_path}")
    print(f"Summary exported to: {summary_path}")
    print(json.dumps(summary, indent=2))


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="NIFTY short straddle backtest using Dhan historical API")
    parser.add_argument("--start-date", type=str, default=None, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end-date", type=str, default=None, help="End date (YYYY-MM-DD)")
    parser.add_argument("--output-dir", type=str, default="output", help="Directory for backtest exports")
    parser.add_argument(
        "--stoploss-pct",
        type=float,
        default=STOPLOSS_PCT,
        help="Combined premium stoploss as decimal (default: 0.25)",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    end_date = datetime.strptime(args.end_date, "%Y-%m-%d").date() if args.end_date else date.today()
    start_date = (
        datetime.strptime(args.start_date, "%Y-%m-%d").date()
        if args.start_date
        else end_date - timedelta(days=3 * 365)
    )

    client_id = get_required_env("DHAN_CLIENT_ID")
    access_token = get_required_env("DHAN_ACCESS_TOKEN")

    adapter = DhanHistoricalAdapter(client_id=client_id, access_token=access_token)
    trades = run_backtest(adapter=adapter, start_date=start_date, end_date=end_date, stoploss_pct=args.stoploss_pct)
    export_results(trades=trades, output_dir=Path(args.output_dir))


if __name__ == "__main__":
    main()
