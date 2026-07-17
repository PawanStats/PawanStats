import unittest
from datetime import date, datetime

from nifty_short_straddle_backtest import (
    Candle,
    nearest_weekly_expiry,
    run_backtest,
    select_atm_strike,
)


class FakeAdapter:
    def __init__(self, stoploss_hit: bool):
        self.stoploss_hit = stoploss_hit

    def get_spot_candles(self, trading_date):
        return [
            Candle(datetime(2026, 1, 1, 9, 16), 22496.0),
            Candle(datetime(2026, 1, 1, 9, 17), 22510.0),
        ]

    def get_weekly_expiries(self, as_of_date):
        return [date(2026, 1, 8), date(2026, 1, 15)]

    def get_option_candles(self, trading_date, expiry, strike, option_type):
        if self.stoploss_hit:
            prices = [100.0, 130.0] if option_type == "CE" else [100.0, 121.0]
            times = [datetime(2026, 1, 1, 9, 17), datetime(2026, 1, 1, 9, 45)]
        else:
            prices = [100.0, 95.0] if option_type == "CE" else [100.0, 90.0]
            times = [datetime(2026, 1, 1, 9, 17), datetime(2026, 1, 1, 15, 10)]

        return [Candle(ts, px) for ts, px in zip(times, prices)]


class StrategyLogicTests(unittest.TestCase):
    def test_select_atm_strike_rounds_to_nearest_step(self):
        self.assertEqual(select_atm_strike(22524.0), 22500)
        self.assertEqual(select_atm_strike(22525.0), 22550)

    def test_nearest_weekly_expiry_prefers_available_future_expiry(self):
        expiry = nearest_weekly_expiry(
            date(2026, 1, 6),
            expiries=[date(2026, 1, 8), date(2026, 1, 15)],
        )
        self.assertEqual(expiry, date(2026, 1, 8))

    def test_backtest_exits_on_combined_stoploss(self):
        trades = run_backtest(FakeAdapter(stoploss_hit=True), date(2026, 1, 1), date(2026, 1, 1))
        self.assertEqual(len(trades), 1)
        trade = trades[0]
        self.assertEqual(trade.exit_reason, "stoploss")
        self.assertEqual(trade.strike, 22500)

    def test_backtest_uses_time_exit_when_stoploss_not_hit(self):
        trades = run_backtest(FakeAdapter(stoploss_hit=False), date(2026, 1, 1), date(2026, 1, 1))
        self.assertEqual(len(trades), 1)
        trade = trades[0]
        self.assertEqual(trade.exit_reason, "time_exit")
        self.assertEqual(trade.exit_time.time().hour, 15)
        self.assertEqual(trade.exit_time.time().minute, 10)


if __name__ == "__main__":
    unittest.main()
