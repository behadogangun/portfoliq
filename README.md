# PortfoliQ 📈

> A full-stack investment portfolio tracker built with Django — featuring real-time market data, AI-powered insights, advanced analytics, and 30+ unique features.

![Python](https://img.shields.io/badge/Python-3.14-blue?logo=python&logoColor=white)
![Django](https://img.shields.io/badge/Django-6.0-green?logo=django&logoColor=white)
![Tests](https://img.shields.io/badge/Tests-159%20passing-brightgreen?logo=pytest)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-purple?logo=bootstrap&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-yellow)
![Status](https://img.shields.io/badge/Status-Production%20Ready-success)

---

## 📋 Table of Contents

- [Features](#-features)
- [Tech Stack](#-tech-stack)
- [Installation](#-installation)
- [Environment Variables](#-environment-variables)
- [Project Structure](#-project-structure)
- [URL Map](#-url-map)
- [API Endpoints](#-api-endpoints)
- [Tests](#-tests)
- [Deploy](#-deploy)

---

## 🚀 Features

### 📊 Core Portfolio Management
- **Multi-portfolio support** — Create and manage unlimited portfolios
- **Asset tracking** — Stocks, crypto, gold, currency, and other asset types
- **Transaction history** — Full buy/sell log with automatic weighted avg. price calculation
- **Real-time prices** — Live data via CoinGecko, yfinance, Alpha Vantage APIs
- **Price History** — Stored per-asset price snapshots for historical analysis
- **CSV & PDF export** — Professional portfolio reports with ReportLab
- **Watchlist** — Track assets without owning them
- **Price Alerts** — AJAX-powered alerts with toast notifications (checks every 60s)

### 🧠 Portfolio Intelligence
- **Portfolio Health Score** — A–D letter grade with 4 sub-scores: Diversification, Concentration Risk, Profitability, Risk Management
- **Portfolio DNA** — Analyzes your allocation and assigns an investor personality: Crypto Maximalist, Stock Market Pro, Safe Haven Seeker, Balanced Innovator, Alpha Hunter, Diamond Hands, Cautious Strategist
- **Smart Rebalancing** — Suggests buy/reduce actions to hit ideal allocation targets
- **Correlation Matrix** — Pearson correlation between all your assets using price history
- **Fear & Greed Index** — Live Alternative.me crypto sentiment with emoji gauge

### 📈 Advanced Analytics
- **Portfolio Beta** — Weighted beta vs. S&P 500 (SPY) using 1-year daily returns
- **Portfolio Volatility Chart** — 10-day rolling annualized volatility over 3 months
- **Monte Carlo Simulation** — Up to 1,000 random simulations of future portfolio value with histogram distribution and 5th/25th/50th/75th/95th percentile outcomes
- **Efficient Frontier** — Markowitz risk/return optimization with 300 random portfolios, Max Sharpe and Min Risk portfolio detection, scatter chart visualization
- **Risk Analysis per Asset** — Sharpe ratio, annualized volatility, max drawdown, total return, avg. daily return

### 🛠️ Tools
- **What-If Simulator** — Historical simulation: "What if I invested $X in Y asset Z days ago?"
- **Regret Calculator** — Side-by-side performance comparison of two assets over the same period
- **Break-Even Calculator** — Progress bars showing how far each asset is from profit
- **DCA Planner** — Dollar Cost Averaging projection with monthly compounding chart
- **Portfolio Comparison** — Compare two of your portfolios side by side with a return bar chart

### 🌍 Market & Research
- **Market Overview** — Top 20 cryptos by market cap with 7-day sparklines + top 20 stocks
- **Market Heatmap** — S&P 500 style colored grid, 5 sectors × 10 stocks
- **Sector Rotation Tracker** — 11 ETF sectors (XLK, XLV, XLF...) with 1D/1W/1M performance
- **Market Mood Ring** — 6 indicators (Fear & Greed, S&P 500, VIX, Bitcoin, Gold, DXY) combined into a 0–100 sentiment score
- **Earnings Calendar** — Upcoming earnings for 20 major S&P 500 companies with days-away color coding
- **Short Squeeze Detector** — 24 high-short-interest stocks ranked by proprietary squeeze score
- **Economic Calendar** — 25+ macro events (Fed, CPI, NFP, ECB, TCMB) with country flags and impact filtering
- **IPO Tracker** — Upcoming and recent IPOs from NASDAQ calendar API
- **Insider Trading Feed** — Executive buy/sell activity via yfinance SEC filings

### 🏆 Investor Research
- **Portfolio vs Famous Investors** — Daily return comparison vs. Warren Buffett, Cathie Wood (ARK), Ray Dalio (All Weather), Michael Burry
- **Price Targets** — Analyst consensus targets (low/mean/high) with upside % and visual price range bar
- **Dividend Tracker** — Annual/monthly income per stock, dividend yield, payout ratio, recent payment history
- **Crisis Simulator** — Apply 5 historical crises to your portfolio: 2008 Financial Crisis, COVID-19 Crash, 2022 Crypto Winter, Dot-com Bubble, Black Monday 1987 — with per-asset symbol-specific historical drops

### 🇹🇷 Turkey
- **BIST Market** — Top 15 Borsa İstanbul stocks with real-time TRY prices via yfinance (.IS suffix)
- **USD/TRY Rate** — Live exchange rate with portfolio value converted to TRY
- **TCMB Event** — Turkish Central Bank interest rate decision in Economic Calendar

### ✨ UI/UX
- **Apple-inspired design system** — Custom CSS: `pq-card`, `pq-nav`, `btn-apple`, `pq-input`, `pq-table`
- **Dark mode** — Toggle with smooth transition, persisted via localStorage
- **Live ticker band** — 28 symbols scrolling below navbar (BTC, ETH, BNB, SOL, XRP, ADA, DOGE, AVAX + 20 major stocks)
- **Mobile responsive** — Full hamburger menu with scrollable sections
- **Onboarding flow** — 5-step guided modal, localStorage persistent (never repeats)
- **Shareable portfolio card** — Dark card downloadable as PNG via html2canvas
- **Micro-animations** — card-enter fade-in, badge-pulse on profit/loss, page-enter transitions, skeleton-shimmer loading
- **3 Navbar dropdowns** — Analytics (9 items), Tools (7 items), 🇹🇷 Turkey
- **Confetti easter egg** — Triggers when portfolio return exceeds 10%

### ⚡ Performance
- **Django LocMemCache** — 60-second cache on crypto/stock prices; 5-minute cache on market mood; 1-hour cache on earnings and famous portfolios
- **select_related + prefetch_related** — All views optimized to avoid N+1 queries
- **Prefetched ordering** — `PriceHistory.objects.order_by('-timestamp')` in all asset queries

---

## 🧪 Tests

```bash
python manage.py test
```

### ✅ 159 Tests Passing in 118s

| Test Class | Tests | Description |
|---|---|---|
| `PortfolioModelTest` | 17 | Model methods: total_cost, current_value, profit_loss, total_value |
| `PortfolioViewTest` | 18 | CRUD views, auth redirects, search, context data |
| `TransactionTest` | 6 | Buy/sell quantity updates, avg price recalculation |
| `AuthViewTest` | 9 | Login, register, logout, profile, redirects |
| `WatchlistTest` | 5 | Add, remove, duplicate prevention, auth |
| `PriceAlertTest` | 7 | Create, delete, alert types, cross-user security |
| `RiskMetricsTest` | 8 | Sharpe, volatility, drawdown, edge cases |
| `AjaxTest` | 7 | Ticker, search, alert check, auth guards |
| `ExportTest` | 5 | CSV content, PDF content-type, permissions |
| `AnalyticsViewTest` | 30 | All new feature views load correctly |
| `CrisisSimulatorTest` | 7 | 2008, COVID, Crypto Winter, invalid input, empty assets |
| `MarketMoodServiceTest` | 3 | Score range 0-100, indicators present, return type |
| `EconomicCalendarTest` | 3 | List type, required fields, date sorting |
| `FamousInvestorsTest` | 2 | List type, required fields per investor |
| `IntelligenceServiceTest` | 10 | Health score A-D, DNA personality, rebalancing, correlation |
| `CacheTest` | 2 | Cache hit verification on second load |
| `NewFeatureViewTest` | 18 | All tool and tracker pages: status 200 + auth 302 |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| Backend | Django 6.0.5 | Web framework |
| API Framework | Django REST Framework | REST API endpoints |
| Database | SQLite (dev) / PostgreSQL (prod) | Data persistence |
| Frontend | Bootstrap 5.3, Bootstrap Icons | UI components |
| Charts | Chart.js 4.4 | Line, bar, scatter, donut charts |
| Image Export | html2canvas 1.4.1 | Portfolio card PNG download |
| Market Data | yfinance | Stocks, crypto, ETFs, beta, dividends |
| Crypto | CoinGecko API (free tier) | Crypto prices, market data, sparklines |
| Stocks | Alpha Vantage (free tier) | Stock search, gold, currency |
| News | NewsAPI (free tier) | Market and asset-specific news |
| Sentiment | Alternative.me | Fear & Greed Index |
| PDF | ReportLab | Portfolio PDF report generation |
| Cache | Django LocMemCache | In-memory API response caching |
| Auth | Django built-in | Session-based authentication |
| Deploy | Render | Production cloud hosting |
| Python | 3.14.3 | Runtime |

---

## ⚙️ Installation

```bash
# 1. Clone the repository
git clone https://github.com/behadogangun/portfoliq.git
cd portfoliq

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate      # macOS/Linux
# venv\Scripts\activate       # Windows

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create environment file
cp .env.example .env
# Edit .env and add your API keys

# 5. Run database migrations
python manage.py migrate

# 6. (Optional) Create admin superuser
python manage.py createsuperuser

# 7. Start development server
python manage.py runserver
```

Open `http://127.0.0.1:8000` in your browser.

---

## 🔑 Environment Variables

Create a `.env` file in the project root:

```env
SECRET_KEY=your-django-secret-key-here
DEBUG=True
ALPHA_VANTAGE_KEY=your-alpha-vantage-key
NEWS_API_KEY=your-newsapi-key
FINNHUB_KEY=your-finnhub-key
```

**Free API Keys:**

| Service | URL | Usage |
|---|---|---|
| Alpha Vantage | https://alphavantage.co | Stock symbol search, gold/currency prices |
| NewsAPI | https://newsapi.org | Market news, asset-specific news |
| Finnhub | https://finnhub.io | Economic calendar events |

> **Note:** yfinance and CoinGecko work without API keys. The app degrades gracefully without them.

---

## 📁 Project Structure

```
portfoliq/
│
├── accounts/                    # Authentication app
│   ├── views.py                 # register, login, logout, profile, change_password
│   ├── forms.py                 # RegisterForm
│   └── urls.py
│
├── api/                         # Django REST Framework
│   ├── views.py                 # PortfolioViewSet, AssetViewSet
│   └── urls.py
│
├── portfolio/                   # Main application
│   ├── models.py                # Portfolio, Asset, Transaction, PriceHistory,
│   │                            # PriceAlert, WatchlistItem
│   ├── views.py                 # 45+ views (1,349 lines)
│   ├── services.py              # All API integrations & business logic (1,400+ lines)
│   │   ├── get_crypto_price / get_crypto_info / search_crypto
│   │   ├── get_stock_info / search_stocks
│   │   ├── get_gold_price / get_currency_price
│   │   ├── fetch_price / fetch_asset_info
│   │   ├── get_top_cryptos / get_top_stocks
│   │   ├── get_asset_news / get_market_news
│   │   ├── calculate_risk_metrics
│   │   ├── get_fear_greed_index
│   │   ├── calculate_portfolio_health
│   │   ├── get_smart_rebalancing
│   │   ├── get_historical_price
│   │   ├── get_correlation_matrix
│   │   ├── calculate_portfolio_dna
│   │   ├── get_dividend_info
│   │   ├── calculate_portfolio_beta
│   │   ├── get_sector_rotation
│   │   ├── get_ipo_calendar
│   │   ├── get_insider_trading
│   │   ├── get_price_targets
│   │   ├── get_portfolio_volatility
│   │   ├── monte_carlo_simulation
│   │   ├── calculate_efficient_frontier
│   │   ├── get_tcmb_rate / get_bist_stock / get_bist_overview
│   │   ├── get_economic_calendar
│   │   ├── get_market_mood
│   │   ├── get_earnings_calendar
│   │   ├── get_short_squeeze_candidates
│   │   ├── get_famous_portfolios
│   │   └── crisis_simulator
│   ├── forms.py                 # PortfolioForm, AssetForm, TransactionForm
│   ├── urls.py                  # 45+ URL patterns
│   ├── admin.py                 # All models registered
│   ├── tests.py                 # 159 tests across 17 test classes
│   └── templatetags/
│       └── filters.py           # format_currency, format_price, format_number,
│                                # format_quantity, split, index, convert_currency
│
├── templates/
│   ├── base.html                # Navbar (3 dropdowns), live ticker, dark mode,
│   │                            # onboarding modal, mobile menu
│   ├── accounts/
│   │   ├── login.html
│   │   ├── register.html
│   │   └── profile.html
│   └── portfolio/               # 35+ templates
│       ├── landing.html         ├── intelligence.html
│       ├── dashboard.html       ├── whatif.html
│       ├── portfolio_list.html  ├── regret.html
│       ├── portfolio_detail.html├── breakeven.html
│       ├── portfolio_card.html  ├── heatmap.html
│       ├── asset_form.html      ├── dca_planner.html
│       ├── asset_detail.html    ├── dividend_tracker.html
│       ├── market.html          ├── portfolio_beta.html
│       ├── watchlist.html       ├── sector_rotation.html
│       ├── alerts.html          ├── ipo_tracker.html
│       ├── news.html            ├── insider_trading.html
│       ├── price_targets.html   ├── volatility_chart.html
│       ├── portfolio_comparison.html  ├── monte_carlo.html
│       ├── efficient_frontier.html    ├── bist_market.html
│       ├── economic_calendar.html     ├── market_mood.html
│       ├── earnings_calendar.html     ├── short_squeeze.html
│       ├── famous_investors.html      └── crisis_sim.html
│
├── portfoliq/
│   ├── settings.py              # Django settings with LocMemCache
│   ├── urls.py
│   ├── wsgi.py
│   └── asgi.py
│
├── .gitignore
├── manage.py
├── requirements.txt
└── README.md
```

---

## 🗺️ URL Map

```
/                        → Landing page
/dashboard/              → Main dashboard
/portfolios/             → Portfolio list (search + pagination)
/portfolios/new/         → Create portfolio
/portfolios/<pk>/        → Portfolio detail
/portfolios/<pk>/edit/   → Edit portfolio
/portfolios/<pk>/delete/ → Delete portfolio
/portfolios/<pk>/card/   → Shareable portfolio card

/assets/<pk>/            → Asset detail
/assets/<pk>/delete/     → Delete asset
/assets/<pk>/transaction/→ Add transaction

/market/                 → Market overview
/watchlist/              → Watchlist
/alerts/                 → Price alerts
/news/                   → Market news

/intelligence/           → Portfolio Intelligence
/whatif/                 → What-If Simulator
/regret/                 → Regret Calculator
/breakeven/              → Break-Even Calculator
/heatmap/                → Market Heatmap
/dca/                    → DCA Planner
/dividends/              → Dividend Tracker
/beta/                   → Portfolio Beta
/sectors/                → Sector Rotation
/ipo/                    → IPO Tracker
/insider/                → Insider Trading Feed
/targets/                → Price Targets
/volatility/             → Volatility Chart
/compare/                → Portfolio Comparison
/monte-carlo/            → Monte Carlo Simulation
/efficient-frontier/     → Efficient Frontier
/bist/                   → BIST Market
/calendar/               → Economic Calendar
/mood/                   → Market Mood Ring
/earnings/               → Earnings Calendar
/short-squeeze/          → Short Squeeze Detector
/famous/                 → Famous Investors
/crisis/                 → Crisis Simulator

/export/<pk>/csv/        → CSV export
/export/<pk>/pdf/        → PDF export

/ajax/ticker/            → Live ticker (JSON)
/ajax/search/            → Asset search (JSON)
/ajax/info/              → Asset info (JSON)
/ajax/check-alerts/      → Triggered alerts (JSON)
/ajax/refresh/<pk>/      → Refresh prices (JSON)

/api/portfolios/         → DRF portfolios
/api/assets/             → DRF assets
/admin/                  → Django admin
```

---

## 🔌 REST API (DRF)

```http
GET  /api/portfolios/      → List user portfolios
GET  /api/portfolios/<id>/ → Portfolio detail
GET  /api/assets/          → List user assets
GET  /api/assets/<id>/     → Asset detail
```

All endpoints require session authentication. Returns JSON.

---

## 🚀 Deploy on Render

1. Push code to GitHub
2. Go to [render.com](https://render.com) → New Web Service
3. Connect your GitHub repo
4. Set **build command:**
   ```bash
   pip install -r requirements.txt && python manage.py migrate
   ```
5. Set **start command:**
   ```bash
   gunicorn portfoliq.wsgi:application
   ```
6. Add environment variables in Render dashboard
7. Deploy!

---

## 📦 Key Dependencies

```
django>=6.0
djangorestframework
yfinance
requests
python-dotenv
reportlab
gunicorn
whitenoise
numpy
pandas
```

Full list in `requirements.txt`.

---

## 📄 License

MIT License — feel free to use, modify, and distribute.

---

## 👤 Author

**Beha Doğangun**
- GitHub: [@behadogangun](https://github.com/behadogangun)

---

> Built with ❤️ as a term project for ACM 412 — Django & Web Technologies