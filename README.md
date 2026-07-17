Hi ![](https://user-images.githubusercontent.com/18350557/176309783-0785949b-9127-417c-8b55-ab5a4333674e.gif) My name is Pawan Dighore
======================================================================================================================================

Full Stack AI Developer  
------------------------------------------------
​I am currently a Full-Stack AI Developer  focused on creating AI-driven applications and agentic automation. I work with Python and modern web tools to build backend services, integrate LLMs, and automate real-world workflows. I also have a strong interest in trading technology and financial systems.


* 🌍  I'm based in India
* ✉️  You can contact me at [pawandighore22@gmail.com](mailto:pawandighore22@gmail.com)
* 🧠  I'm currently learning Multi-agent AI workflows and Low-latency financial systems.
* 👥 I'm looking to collaborate on Autonomous AI agents, Full Stack AI architectures, and real-time financial data platforms.
* 💬  Ask me about I don't just write code; I build systems that eliminate manual work and solve complexities.
## 🔗Social:
[![LinkedIn](https://img.shields.io/badge/LinkedIn-%230077B5.svg?logo=linkedin&logoColor=white)][![email](https://img.shields.io/badge/Email-D14836?logo=gmail&logoColor=white)]

 
## 💻 Tech Stack: 
### 👨‍💻 Languages
![Java](https://img.shields.io/badge/java-%23ED8B00.svg?style=plastic&logo=openjdk&logoColor=white) ![Python](https://img.shields.io/badge/python-3670A0?style=plastic&logo=python&logoColor=ffdd54) 

### 🎨 Frontend
 ![React](https://img.shields.io/badge/react-%2320232a.svg?style=plastic&logo=react&logoColor=%2361DAFB) ![Vite](https://img.shields.io/badge/vite-%23646CFF.svg?style=plastic&logo=vite&logoColor=white) 
### ⚙️ Backend & Frameworks
![Express.js](https://img.shields.io/badge/express.js-%23404d59.svg?style=plastic&logo=express&logoColor=%2361DAFB) ![FastAPI](https://img.shields.io/badge/FastAPI-005571?style=plastic&logo=fastapi) ![NodeJS](https://img.shields.io/badge/node.js-6DA55F?style=plastic&logo=node.js&logoColor=white)
### ☁️ Cloud & Database
![Render](https://img.shields.io/badge/Render-%46E3B7.svg?style=plastic&logo=render&logoColor=white) ![Oracle](https://img.shields.io/badge/Oracle-F80000?style=plastic&logo=oracle&logoColor=white) ![Google Cloud](https://img.shields.io/badge/GoogleCloud-%234285F4.svg?style=plastic&logo=google-cloud&logoColor=white) ![Anaconda](https://img.shields.io/badge/Anaconda-%2344A833.svg?style=plastic&logo=anaconda&logoColor=white) ![MySQL](https://img.shields.io/badge/mysql-4479A1.svg?style=plastic&logo=mysql&logoColor=white) ![Firebase](https://img.shields.io/badge/firebase-a08021?style=plastic&logo=firebase&logoColor=ffcd34)
### 🧠 AI / ML
![Matplotlib](https://img.shields.io/badge/Matplotlib-%23ffffff.svg?style=plastic&logo=Matplotlib&logoColor=black) ![NumPy](https://img.shields.io/badge/numpy-%23013243.svg?style=plastic&logo=numpy&logoColor=white) ![Pandas](https://img.shields.io/badge/pandas-%23150458.svg?style=plastic&logo=pandas&logoColor=white) ![scikit-learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=plastic&logo=scikit-learn&logoColor=white) ![TensorFlow](https://img.shields.io/badge/TensorFlow-%23FF6F00.svg?style=plastic&logo=TensorFlow&logoColor=white)
### 🛠 Tools
![GitHub](https://img.shields.io/badge/github-%23121011.svg?style=plastic&logo=github&logoColor=white) ![Git](https://img.shields.io/badge/git-%23F05033.svg?style=plastic&logo=git&logoColor=white)


## 🏆 GitHub Trophies
![](https://github-profile-trophy.vercel.app/?username=PawanStats&theme=radical&no-frame=false&no-bg=false&margin-w=4)

<p align="center">
  <img src="https://github.githubassets.com/images/modules/profile/achievements/pull-shark-default.png" width="120" />
  <img src="https://github.githubassets.com/images/modules/profile/achievements/yolo-default.png" width="120" />
  <img src="https://github.githubassets.com/images/modules/profile/achievements/quickdraw-default.png" width="120" />
</p>

<p align="center">
  <b>🦈 Pull Shark</b> &nbsp; | &nbsp;
  <b>🎯 YOLO</b> &nbsp; | &nbsp;
  <b>⚡ Quickdraw</b>
</p>

<!-- Snake Game Repo View -->

<div align="center">
  <img src="https://profile-readme-generator.com/assets/snake.svg" alt="Snake animation" />
</div>

### ✍️ Random Dev Quote
![](https://quotes-github-readme.vercel.app/api?type=horizontal&theme=radical)

[![](https://visitcount.itsvg.in/api?id=PawanStats&icon=5&color=0)](https://visitcount.itsvg.in)

<!-- Proudly created with GPRM ( https://gprm.itsvg.in ) -->

## NIFTY 50 Short Straddle Backtest (Dhan API)

A Python backtest is available at:

- `/home/runner/work/PawanStats/PawanStats/nifty_short_straddle_backtest.py`

### Strategy implemented

- Underlying reference: NIFTY spot/index
- Entry: 09:17 AM
- Position: Short ATM CE + Short ATM PE (same strike, same nearest weekly expiry)
- Stoploss: Exit both legs if combined premium rises by 25% from entry
- Time exit: Buy back the original sold CE and PE at 03:10 PM if stoploss is not hit
- Lookback default: last 3 years

### Credentials (environment variables)

```bash
export DHAN_CLIENT_ID="your_client_id"
export DHAN_ACCESS_TOKEN="your_access_token"
```

### Run

```bash
python /home/runner/work/PawanStats/PawanStats/nifty_short_straddle_backtest.py
```

Optional arguments:

```bash
python /home/runner/work/PawanStats/PawanStats/nifty_short_straddle_backtest.py \
  --start-date 2023-01-01 \
  --end-date 2026-01-01 \
  --stoploss-pct 0.25 \
  --output-dir /home/runner/work/PawanStats/PawanStats/output
```

### Output

- `nifty_short_straddle_trades.csv` (trade-level results)
- `nifty_short_straddle_summary.json` (summary metrics)

### Dhan endpoint configuration

If your Dhan account/API version uses different endpoint paths or payload fields, update the `DhanAPIConfig` and request payload mapping in the adapter section of `nifty_short_straddle_backtest.py`.
