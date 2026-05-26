# PortfoliQ 📈

> A full-stack investment portfolio tracker built with Django — featuring real-time market data, AI-powered insights, advanced analytics, and 30+ unique features.

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python)
![Django](https://img.shields.io/badge/Django-6.0-green?logo=django)
![Tests](https://img.shields.io/badge/Tests-159%20passing-brightgreen)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## 🚀 Features

### 📊 Core Portfolio Management
- **Multi-portfolio support** — Create and manage multiple portfolios
- **Asset tracking** — Stocks, crypto, gold, currency, and more
- **Transaction history** — Buy/sell tracking with automatic avg. price calculation
- **Real-time prices** — Live data from CoinGecko, yfinance, Alpha Vantage
- **CSV & PDF export** — Download portfolio reports

### 🧠 Portfolio Intelligence
- **Portfolio Health Score** — A–D grade with 4 sub-metrics
- **Portfolio DNA** — Discover your investor personality (Crypto Maximalist, Stock Market Pro, etc.)
- **Smart Rebalancing** — AI-suggested target allocations
- **Correlation Matrix** — See how your assets move together
- **Fear & Greed Index** — Live crypto market sentiment

### 📈 Advanced Analytics
- **Portfolio Beta** — Measure volatility vs. S&P 500
- **Volatility Chart** — 10-day rolling annualized volatility
- **Monte Carlo Simulation** — 500 simulations of future portfolio value
- **Efficient Frontier** — Risk/return optimization (Markowitz)
- **Risk Analysis** — Sharpe ratio, max drawdown, volatility per asset

### 🛠️ Tools
- **What-If Simulator** — "What if I invested $1000 in BTC 1 year ago?"
- **Regret Calculator** — Compare two assets side by side
- **Break-Even Calculator** — See how far each asset is from profit
- **DCA Planner** — Dollar cost averaging growth projection
- **Portfolio Comparison** — Compare two portfolios side by side

### 🌍 Market & Research
- **Market Overview** — Top 20 cryptos + top 20 stocks
- **Market Heatmap** — S&P 500 style sector heatmap
- **Sector Rotation Tracker** — 11 ETF sectors with 1D/1W/1M performance
- **Market Mood Ring** — 6+ indicators combined into one market sentiment score
- **Earnings Calendar** — Upcoming earnings reports with days-away alerts
- **Short Squeeze Detector** — High short interest stocks ranked by squeeze score
- **Economic Calendar** — Key macro events with impact ratings
- **IPO Tracker** — Upcoming and recent IPOs from NASDAQ
- **Insider Trading Feed** — Executive buy/sell activity

### 🏆 Investor Research
- **Portfolio vs Famous Investors** — Compare daily returns vs Buffett, ARK, Ray Dalio, Burry
- **Price Targets** — Analyst consensus targets with upside/downside visualization
- **Dividend Tracker** — Annual/monthly income from dividend stocks
- **Crisis Simulator** — See what 2008, COVID, Crypto Winter, Dot-com would do to your portfolio

### 🇹🇷 Turkey
- **BIST Market** — Top 15 Borsa İstanbul stocks with TRY prices
- **USD/TRY Rate** — Live exchange rate + portfolio value in TRY

### ✨ UI/UX
- **Apple-inspired design** — Clean, minimal, professional
- **Dark mode** — Persistent across sessions
- **Live ticker** — 28 symbols scrolling in real-time (BTC, ETH, AAPL, TSLA, NVDA...)
- **Mobile responsive** — Full hamburger menu on mobile
- **Onboarding flow** — 5-step guided tour for new users
- **Shareable portfolio card** — Download your portfolio as a beautiful dark card image
- **Micro-animations** — Card entrance, badge pulse, page transitions
- **Skeleton loading** — Smooth placeholder animations

### ⚡ Performance
- **Django cache** — 60-second caching on all API calls
- **select_related + prefetch_related** — Optimized ORM queries
- **Watchlist & Price Alerts** — AJAX-powered with toast notifications

---

## 🧪 Tests

```bash
python manage.py test
```

**159 tests passing** across 12 test classes:
- Model tests, View tests, Auth tests
- Transaction tests, Watchlist tests, Alert tests
- Risk metrics, AJAX, Export, Intelligence
- Crisis Simulator, Market Mood, Economic Calendar

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Django 6.0, Django REST Framework |
| Database | SQLite (dev) / PostgreSQL (prod) |
| Frontend | Bootstrap 5, Chart.js, html2canvas |
| Market Data | yfinance, CoinGecko API, Alpha Vantage |
| News | NewsAPI |
| Sentiment | Alternative.me Fear & Greed |
| PDF | ReportLab |
| Auth | Django built-in |
| Cache | Django LocMemCache |
| Deploy | Render |

---

## ⚙️ Installation

```bash
# Clone the repo
git clone https://github.com/behadogangun/portfoliq.git
cd portfoliq

# Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Create .env file
cp .env.example .env
# Add your API keys to .env

# Run migrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Run development server
python manage.py runserver
```

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key
DEBUG=True
ALPHA_VANTAGE_KEY=your-alpha-vantage-key
NEWS_API_KEY=your-newsapi-key
FINNHUB_KEY=your-finnhub-key
```

**Free API Keys:**
- [Alpha Vantage](https://www.alphavantage.co/support/#api-key) — Stock search
- [NewsAPI](https://newsapi.org/register) — Market news
- [Finnhub](https://finnhub.io/register) — Economic calendar

---

## 📁 Project Structure

```
portfoliq/
├── accounts/          # Auth: login, register, profile
├── api/               # Django REST Framework endpoints
├── portfolio/
│   ├── models.py      # Portfolio, Asset, Transaction, PriceHistory, PriceAlert, WatchlistItem
│   ├── views.py       # 40+ views
│   ├── services.py    # All API integrations & business logic
│   ├── urls.py        # URL routing
│   ├── tests.py       # 159 tests
│   └── templatetags/
│       └── filters.py # Custom template filters
├── templates/
│   ├── base.html      # Navbar, ticker, dark mode, onboarding
│   └── portfolio/     # 35+ templates
├── portfoliq/
│   ├── settings.py
│   └── urls.py
├── requirements.txt
└── manage.py
```

---

## 🌐 API Endpoints

```
GET  /api/portfolios/          # List portfolios (DRF)
GET  /api/assets/              # List assets (DRF)
GET  /ajax/ticker/             # Live ticker data
GET  /ajax/search/?q=          # Asset search
GET  /ajax/info/?symbol=&type= # Asset info
GET  /ajax/check-alerts/       # Check triggered alerts
```

---

## 🗺️ URL Map

```
/dashboard/              /intelligence/         /bist/
/portfolios/             /whatif/               /mood/
/market/                 /regret/               /earnings/
/watchlist/              /breakeven/            /short-squeeze/
/alerts/                 /heatmap/              /famous/
/news/                   /dca/                  /crisis/
/beta/                   /dividends/            /calendar/
/sectors/                /targets/              /efficient-frontier/
/ipo/                    /compare/              /monte-carlo/
/insider/                /volatility/
```

---

## 📸 Screenshots

> Dashboard · Portfolio Intelligence · Market Mood Ring · Crisis Simulator · Efficient Frontier

---

## 🚀 Deploy

Deployed on **Render** — [Live Demo](#)

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

## 👤 Author

**Beha Doğangun**
- GitHub: [@behadogangun](https://github.com/behadogangun)

---

> Built with ❤️ as a term project for ACM 412 — Django & Web Technologies