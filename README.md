# PortfoliQ 📈

**Full-stack investment portfolio tracker built with Django**

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com)
[![Tests](https://img.shields.io/badge/Tests-159%20Passing-2ea44f?style=for-the-badge&logo=pytest&logoColor=white)](#-tests)
[![License](https://img.shields.io/badge/License-MIT-F7B731?style=for-the-badge)](LICENSE)

[🐛 Report Bug](https://github.com/behadogangun/portfoliq/issues) · [💡 Request Feature](https://github.com/behadogangun/portfoliq/issues)

---

## 📖 About

PortfoliQ is a full-stack investment portfolio tracker that gives individual investors access to tools previously only available on professional platforms. It combines real-time market data from multiple APIs with AI-powered analytics, advanced simulations, and a clean Apple-inspired UI.

---

## ✨ Features

### 📊 Portfolio Management

- ✅ Multi-portfolio support with search and pagination
- ✅ Asset types: Stocks · Crypto · Gold · Currency · Other
- ✅ Transaction history with automatic weighted avg. price calculation
- ✅ Real-time price refresh via AJAX
- ✅ CSV & PDF export with ReportLab
- ✅ Watchlist with instant add/remove
- ✅ Price Alerts — AJAX polling every 60 seconds with toast notifications
- ✅ Shareable portfolio card — downloadable dark PNG via html2canvas

### 🧠 Portfolio Intelligence

- ✅ **Health Score** — A–D letter grade with 4 sub-metrics: Diversification, Concentration Risk, Profitability, Risk Management
- ✅ **Portfolio DNA** — Investor personality: Crypto Maximalist, Stock Market Pro, Safe Haven Seeker, Balanced Innovator, Alpha Hunter, Diamond Hands, Cautious Strategist
- ✅ **Smart Rebalancing** — Buy/reduce suggestions to reach ideal allocation
- ✅ **Correlation Matrix** — Pearson correlation between all assets using price history
- ✅ **Fear & Greed Index** — Live Alternative.me sentiment with emoji gauge

### 📈 Advanced Analytics

- ✅ **Portfolio Beta** — Weighted beta vs. S&P 500 using 1-year daily returns
- ✅ **Volatility Chart** — 10-day rolling annualized volatility over 3 months
- ✅ **Monte Carlo Simulation** — Up to 1,000 random path simulations with histogram distribution and 5th/25th/50th/75th/95th percentile outcomes
- ✅ **Efficient Frontier** — Markowitz risk/return optimization with 300 random portfolios, Max Sharpe and Min Risk detection
- ✅ **Risk per Asset** — Sharpe ratio, max drawdown, annualized volatility, avg daily return

### 🛠️ Tools

- ✅ **What-If Simulator** — "What if I invested $X in Y asset Z days ago?"
- ✅ **Regret Calculator** — Side-by-side performance comparison of two assets
- ✅ **Break-Even Calculator** — Progress bars showing distance to profit per asset
- ✅ **DCA Planner** — Dollar Cost Averaging monthly projection with Chart.js
- ✅ **Portfolio Comparison** — Compare two portfolios: value, P&L, return, best pick

### 🌍 Market & Research

- ✅ **Market Overview** — Top 20 cryptos with 7-day sparklines + top 20 stocks
- ✅ **Market Heatmap** — S&P 500 style colored grid, 5 sectors × 10 stocks
- ✅ **Sector Rotation Tracker** — 11 ETF sectors (XLK, XLV, XLF...) with 1D/1W/1M performance
- ✅ **Market Mood Ring** — 6 indicators combined into a 0–100 sentiment score: Fear & Greed, S&P 500, VIX, Bitcoin, Gold, DXY
- ✅ **Earnings Calendar** — Upcoming reports for 20 S&P 500 companies with color-coded days-away alerts
- ✅ **Short Squeeze Detector** — 24 high-short-interest stocks ranked by squeeze score (short %, days to cover, volume ratio)
- ✅ **Economic Calendar** — 25+ macro events with country flags and high/medium/low impact filtering
- ✅ **IPO Tracker** — Upcoming and recent IPOs from NASDAQ API
- ✅ **Insider Trading Feed** — Executive buy/sell activity from SEC filings via yfinance

### 🏆 Investor Research

- ✅ **Portfolio vs Famous Investors** — Daily return comparison vs. Warren Buffett, Cathie Wood (ARK), Ray Dalio (All Weather), Michael Burry with real holdings and weights
- ✅ **Price Targets** — Analyst consensus (low/mean/high) with upside % and visual price range bar
- ✅ **Dividend Tracker** — Annual/monthly income, yield, payout ratio, last 8 payments
- ✅ **Crisis Simulator** — Apply 5 historical crashes to your portfolio with per-symbol historical drops:
  - 🏦 2008 Financial Crisis (S&P -56.8%)
  - 🦠 COVID-19 Crash (S&P -34% in 33 days)
  - ❄️ 2022 Crypto Winter (BTC -77%)
  - 💻 Dot-com Bubble (NASDAQ -78%)
  - 🖤 Black Monday 1987 (S&P -22.6% in one day)

### 🇹🇷 Turkey

- ✅ **BIST Market** — Top 15 Borsa İstanbul stocks with live TRY prices via yfinance `.IS` suffix
- ✅ **USD/TRY Rate** — Live exchange rate with portfolio value converted to Turkish Lira
- ✅ **TCMB Calendar** — Central bank rate decisions included in Economic Calendar

### 🎨 UI & UX

- ✅ Apple-inspired design system — custom CSS: `pq-card`, `btn-apple`, `pq-nav`, `pq-input`, `pq-table`
- ✅ Dark / Light mode — localStorage persistent, smooth transition
- ✅ Live ticker band — 28 symbols scrolling below navbar (BTC, ETH, BNB, SOL, XRP, ADA, DOGE, AVAX + 20 major stocks)
- ✅ Mobile responsive — hamburger menu with Analytics · Tools · Turkey sections
- ✅ Onboarding flow — 5-step guided modal, never repeats (localStorage)
- ✅ Micro-animations — card-enter, badge-pulse, page-enter, skeleton-shimmer
- ✅ 3 Navbar dropdowns — Analytics, Tools, 🇹🇷 Turkey
- ✅ Confetti easter egg — triggers when portfolio return exceeds 10%

### ⚡ Performance

- ✅ Django LocMemCache — 60s cache on crypto/stock prices, 5min on market mood, 1hr on earnings and famous portfolios
- ✅ `select_related` + `prefetch_related` on all views — no N+1 queries
- ✅ `PriceHistory.objects.order_by('-timestamp')` prefetched in all asset queries

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Django 6.0.5, Django REST Framework | Web framework, REST API |
| **Database** | SQLite (dev) / PostgreSQL (prod) | Data persistence |
| **Frontend** | Bootstrap 5.3, Bootstrap Icons | UI components |
| **Charts** | Chart.js 4.4 | Line, Bar, Scatter, Donut |
| **Market Data** | yfinance, CoinGecko API, Alpha Vantage | Stocks, Crypto, ETFs |
| **News** | NewsAPI | Market and asset-specific news |
| **Sentiment** | Alternative.me | Fear & Greed Index |
| **PDF** | ReportLab | Portfolio report generation |
| **Image Export** | html2canvas 1.4.1 | Portfolio card PNG download |
| **Cache** | Django LocMemCache | In-memory API caching |
| **Auth** | Django built-in | Session-based authentication |
| **Python** | 3.14.3 | Runtime |

---

## 🧪 Tests

```bash
python manage.py test
```

✅ **159 tests passing** · 17 test classes · ~118 seconds

| Test Class | # | Coverage |
|---|:---:|---|
| `PortfolioModelTest` | 17 | Model methods: total_cost, current_value, profit_loss, edge cases |
| `PortfolioViewTest` | 18 | CRUD, auth redirects, search, context data |
| `TransactionTest` | 6 | Buy/sell quantity updates, avg price recalculation |
| `AuthViewTest` | 9 | Login, register, logout, profile |
| `WatchlistTest` | 5 | Add, remove, duplicate prevention |
| `PriceAlertTest` | 7 | Create, delete, types, cross-user security |
| `RiskMetricsTest` | 8 | Sharpe ratio, volatility, drawdown, edge cases |
| `AjaxTest` | 7 | Ticker, search, alert check, auth guards |
| `ExportTest` | 5 | CSV content, PDF content-type, permissions |
| `AnalyticsViewTest` | 30 | All new feature views: status 200 + auth 302 |
| `CrisisSimulatorTest` | 7 | All 5 crisis scenarios, invalid input, empty assets |
| `MarketMoodServiceTest` | 3 | Score 0–100 range, indicators, return type |
| `EconomicCalendarTest` | 3 | List type, required fields, date sorting |
| `FamousInvestorsTest` | 2 | List type, required fields per investor |
| `IntelligenceServiceTest` | 10 | Health A–D, DNA, rebalancing, correlation |
| `CacheTest` | 2 | Cache hit verification on second load |
| `NewFeatureViewTest` | 18 | All tool and tracker pages load correctly |

---

## 🏗️ Project Structure

| Path | Contents |
|---|---|
| `accounts/` | Auth: login · register · profile · change password |
| `api/` | DRF: PortfolioViewSet · AssetViewSet |
| `portfolio/models.py` | Portfolio · Asset · Transaction · PriceHistory · PriceAlert · WatchlistItem |
| `portfolio/views.py` | 45+ views |
| `portfolio/services.py` | 35+ service functions — all API integrations and business logic |
| `portfolio/urls.py` | 45+ URL patterns |
| `portfolio/tests.py` | 159 tests across 17 test classes |
| `portfolio/templatetags/filters.py` | format_currency · format_price · format_number · format_quantity |
| `templates/base.html` | Navbar (3 dropdowns) · Live ticker · Dark mode · Onboarding modal |
| `templates/portfolio/` | 35 page templates |
| `portfoliq/settings.py` | Django settings with LocMemCache configuration |

---

## 🗺️ URL Map

```
Core
/dashboard/              /portfolios/             /market/
/watchlist/              /alerts/                 /news/

Analytics
/intelligence/           /beta/                   /volatility/
/monte-carlo/            /efficient-frontier/     /heatmap/
/sectors/                /mood/

Tools
/whatif/                 /regret/                 /breakeven/
/dca/                    /dividends/              /targets/
/compare/                /crisis/

Market Intel
/ipo/                    /insider/                /earnings/
/short-squeeze/          /famous/                 /calendar/

Turkey
/bist/

API & Admin
/api/portfolios/         /api/assets/             /admin/
/ajax/ticker/            /ajax/search/            /ajax/check-alerts/
```

---

## 🔌 REST API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/portfolios/` | List user portfolios |
| GET | `/api/portfolios/<id>/` | Portfolio detail |
| GET | `/api/assets/` | List user assets |
| GET | `/api/assets/<id>/` | Asset detail |

All endpoints require session authentication and return JSON.

---

## ⚙️ Installation

```bash
# Clone
git clone https://github.com/behadogangun/portfoliq.git
cd portfoliq

# Virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# Dependencies
pip install -r requirements.txt

# Environment
cp .env.example .env            # Add your API keys

# Database
python manage.py migrate

# Run
python manage.py runserver
```

Open `http://127.0.0.1:8000` in your browser.

---

## 🔑 Environment Variables

```env
SECRET_KEY        = your-django-secret-key
DEBUG             = True
ALPHA_VANTAGE_KEY = your-key     # alphavantage.co  — free tier
NEWS_API_KEY      = your-key     # newsapi.org      — free tier
FINNHUB_KEY       = your-key     # finnhub.io       — free tier
```

> **yfinance** and **CoinGecko** require no API key. The app degrades gracefully without any key.

---

## 📄 License

MIT © 2026 [Beha Doğangun](https://github.com/behadogangun)

---

**PortfoliQ** — Track smarter, invest better. 📈

⭐ If you find this project useful, consider giving it a star!