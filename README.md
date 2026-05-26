<div align="center">

<br/>

```
██████╗  ██████╗ ██████╗ ████████╗███████╗ ██████╗ ██╗     ██╗ ██████╗
██╔══██╗██╔═══██╗██╔══██╗╚══██╔══╝██╔════╝██╔═══██╗██║     ██║██╔═══██╗
██████╔╝██║   ██║██████╔╝   ██║   █████╗  ██║   ██║██║     ██║██║   ██║
██╔═══╝ ██║   ██║██╔══██╗   ██║   ██╔══╝  ██║   ██║██║     ██║██║▄▄ ██║
██║     ╚██████╔╝██║  ██║   ██║   ██║     ╚██████╔╝███████╗██║╚██████╔╝
╚═╝      ╚═════╝ ╚═╝  ╚═╝   ╚═╝   ╚═╝      ╚═════╝ ╚══════╝╚═╝ ╚══▀▀═╝
```

### 📈 Full-Stack Investment Portfolio Tracker

<br/>

[![Python](https://img.shields.io/badge/Python-3.14-3776AB?style=for-the-badge&logo=python&logoColor=white)](https://python.org)
[![Django](https://img.shields.io/badge/Django-6.0-092E20?style=for-the-badge&logo=django&logoColor=white)](https://djangoproject.com)
[![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?style=for-the-badge&logo=bootstrap&logoColor=white)](https://getbootstrap.com)
[![Tests](https://img.shields.io/badge/Tests-159%20Passing-2ea44f?style=for-the-badge&logo=pytest&logoColor=white)](#-tests)
[![License](https://img.shields.io/badge/License-MIT-F7B731?style=for-the-badge)](LICENSE)

<br/>

> *Track stocks · crypto · gold · Real-time prices · AI insights · Advanced analytics*

<br/>

</div>

---

## ✨ What is PortfoliQ?

PortfoliQ is a **full-stack investment portfolio tracker** built with Django. It combines real-time market data from multiple APIs with AI-powered analytics — giving individual investors access to tools previously only available on Bloomberg terminals.

<br/>

<div align="center">

📊 **30+ Features** &nbsp;·&nbsp; 🧠 **AI Insights** &nbsp;·&nbsp; 📈 **Advanced Analytics** &nbsp;·&nbsp; 🇹🇷 **BIST Support** &nbsp;·&nbsp; 🌙 **Dark Mode** &nbsp;·&nbsp; ✅ **159 Tests**

</div>

---

## 🗂️ Features

<table>
<tr>
<td width="50%" valign="top">

**📊 Portfolio Management**
- Multi-portfolio support
- Stocks · Crypto · Gold · Currency
- Transaction history + avg. cost tracking
- Real-time price refresh (AJAX)
- CSV & PDF export via ReportLab
- Watchlist & Price Alerts (60s AJAX check)

**🧠 Intelligence**
- **Health Score** — A–D grade with 4 sub-metrics
- **Portfolio DNA** — Investor personality type
- **Smart Rebalancing** — Target allocation hints
- **Correlation Matrix** — Pearson correlation
- **Fear & Greed Index** — Live Alternative.me

**📈 Advanced Analytics**
- **Portfolio Beta** — Weighted vs. S&P 500
- **Volatility Chart** — 10-day rolling annualized
- **Monte Carlo** — Up to 1,000 path simulations
- **Efficient Frontier** — Markowitz optimization
- **Risk per Asset** — Sharpe · Drawdown · VaR

</td>
<td width="50%" valign="top">

**🛠️ Tools**
- **What-If Simulator** — Historical what if?
- **Regret Calculator** — Two-asset comparison
- **Break-Even** — Progress to profit bar
- **DCA Planner** — Monthly compounding chart
- **Portfolio Compare** — Side-by-side P&L

**🌍 Market & Research**
- **Market Heatmap** — S&P 500 style grid
- **Sector Rotation** — 11 ETF sectors 1D/1W/1M
- **Market Mood Ring** — 6-indicator score 0–100
- **Earnings Calendar** — Color-coded days-away
- **Short Squeeze Detector** — Ranked candidates
- **Economic Calendar** — 25+ macro events + flags
- **IPO Tracker** · **Insider Trading Feed**

**🏆 Investor Research**
- **Famous Investors** — Buffett · ARK · Dalio · Burry
- **Price Targets** — Analyst consensus + upside bar
- **Dividend Tracker** — Annual income per stock
- **Crisis Simulator** — 5 historical crash scenarios

</td>
</tr>
</table>

---

## 🇹🇷 Turkey Features

| | Feature | Description |
|---|---|---|
| 🏛️ | **BIST Market** | Top 15 Borsa İstanbul stocks with live TRY prices |
| 💱 | **USD/TRY Rate** | Live rate · portfolio value converted to Turkish Lira |
| 🏦 | **TCMB Calendar** | Central bank rate decisions in Economic Calendar |

---

## 🎨 UI / UX

| | Feature | Details |
|---|---|---|
| 🍎 | **Apple Design System** | `pq-card` · `btn-apple` · `pq-nav` · `pq-input` · `pq-table` |
| 🌙 | **Dark Mode** | localStorage persistent · smooth CSS transition |
| 📡 | **Live Ticker** | 28 symbols scrolling: BTC · ETH · AAPL · TSLA · NVDA + more |
| 📱 | **Mobile Responsive** | Hamburger menu with Analytics · Tools · Turkey sections |
| 🎯 | **Onboarding Flow** | 5-step guided modal · localStorage persistent |
| 🃏 | **Share Card** | Portfolio as downloadable dark PNG via html2canvas |
| ✨ | **Animations** | card-enter · badge-pulse · page-enter · skeleton-shimmer |
| 🎊 | **Easter Egg** | Confetti when portfolio return exceeds 10% |
| ⚡ | **API Cache** | Django LocMemCache — 60s to 1hr TTL per endpoint |

---

## 🧪 Tests

```bash
python manage.py test
```

<div align="center">

✅ &nbsp; **159 tests passing** &nbsp; · &nbsp; 17 test classes &nbsp; · &nbsp; ~118 seconds

</div>

<br/>

| Test Class | # | Coverage |
|---|:---:|---|
| `PortfolioModelTest` | 17 | Model methods: total_cost, current_value, profit_loss, edge cases |
| `PortfolioViewTest` | 18 | CRUD views, auth redirects, search, context data |
| `TransactionTest` | 6 | Buy/sell quantity updates, avg price recalculation |
| `AuthViewTest` | 9 | Login, register, logout, profile, redirects |
| `WatchlistTest` | 5 | Add, remove, duplicate prevention |
| `PriceAlertTest` | 7 | Create, delete, types, cross-user security |
| `RiskMetricsTest` | 8 | Sharpe ratio, volatility, drawdown, edge cases |
| `AjaxTest` | 7 | Ticker, search, alert check, auth guards |
| `ExportTest` | 5 | CSV content, PDF content-type, permissions |
| `AnalyticsViewTest` | 30 | All new feature views: status 200 + auth 302 |
| `CrisisSimulatorTest` | 7 | 5 crisis scenarios, invalid input, empty assets |
| `MarketMoodServiceTest` | 3 | Score 0–100 range, indicators present, return type |
| `EconomicCalendarTest` | 3 | List type, required fields, date sorting |
| `FamousInvestorsTest` | 2 | List type, required fields per investor |
| `IntelligenceServiceTest` | 10 | Health A–D, DNA, rebalancing, correlation |
| `CacheTest` | 2 | Cache hit verification on second API call |
| `NewFeatureViewTest` | 18 | All tool and tracker pages load correctly |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Backend** | Django 6.0.5 · Django REST Framework | Web framework · REST API |
| **Database** | SQLite (dev) · PostgreSQL (prod) | Data persistence |
| **Frontend** | Bootstrap 5.3 · Bootstrap Icons | UI components |
| **Charts** | Chart.js 4.4 | Line · Bar · Scatter · Donut |
| **Market Data** | yfinance · CoinGecko API · Alpha Vantage | Stocks · Crypto · ETFs |
| **News** | NewsAPI | Market & asset-specific news |
| **Sentiment** | Alternative.me | Fear & Greed Index |
| **PDF** | ReportLab | Portfolio report generation |
| **Image Export** | html2canvas 1.4.1 | Portfolio card PNG download |
| **Cache** | Django LocMemCache | In-memory API response caching |
| **Auth** | Django built-in | Session-based authentication |
| **Python** | 3.14.3 | Runtime |

---

## ⚙️ Installation

```bash
# 1 — Clone
git clone https://github.com/behadogangun/portfoliq.git
cd portfoliq

# 2 — Virtual environment
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate

# 3 — Dependencies
pip install -r requirements.txt

# 4 — Environment
cp .env.example .env            # Fill in your API keys

# 5 — Database
python manage.py migrate

# 6 — Run
python manage.py runserver
```

🌐 &nbsp; Open **http://127.0.0.1:8000**

---

## 🔑 Environment Variables

```env
SECRET_KEY        = your-django-secret-key
DEBUG             = True
ALPHA_VANTAGE_KEY = your-key     # alphavantage.co — free tier
NEWS_API_KEY      = your-key     # newsapi.org     — free tier
FINNHUB_KEY       = your-key     # finnhub.io      — free tier
```

> **yfinance** and **CoinGecko** require no API key — app works without them.

---

## 📁 Project Structure

```
portfoliq/
│
├── accounts/                    # Auth: login · register · profile
├── api/                         # DRF: PortfolioViewSet · AssetViewSet
│
├── portfolio/
│   ├── models.py                # Portfolio · Asset · Transaction
│   │                            # PriceHistory · PriceAlert · WatchlistItem
│   ├── views.py                 # 45+ views
│   ├── services.py              # 35+ service functions (1,400+ lines)
│   ├── urls.py                  # 45+ URL patterns
│   ├── tests.py                 # 159 tests · 17 test classes
│   ├── admin.py
│   ├── forms.py
│   └── templatetags/
│       └── filters.py           # format_currency · format_price · format_quantity
│
├── templates/
│   ├── base.html                # Navbar (3 dropdowns) · Ticker · Dark mode · Onboarding
│   ├── accounts/                # login · register · profile
│   └── portfolio/               # 35 templates
│
├── portfoliq/
│   ├── settings.py              # LocMemCache config
│   └── urls.py
│
├── .gitignore
├── manage.py
└── requirements.txt
```

---

## 🗺️ URL Map

```
Core             /dashboard/    /portfolios/    /market/    /watchlist/    /alerts/    /news/

Analytics        /intelligence/    /beta/        /volatility/    /sectors/
                 /monte-carlo/     /efficient-frontier/    /heatmap/    /mood/

Tools            /whatif/    /regret/    /breakeven/    /dca/
                 /dividends/    /targets/    /compare/    /crisis/

Market Intel     /ipo/    /insider/    /earnings/    /short-squeeze/    /famous/    /calendar/

Turkey           /bist/

API              /api/portfolios/    /api/assets/    /admin/
                 /ajax/ticker/       /ajax/search/   /ajax/check-alerts/
```

---

## 🔌 REST API

```http
GET  /api/portfolios/       →  List user portfolios
GET  /api/portfolios/<id>/  →  Portfolio detail
GET  /api/assets/           →  List user assets
GET  /api/assets/<id>/      →  Asset detail
```

> All endpoints require session authentication · Returns JSON

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

<div align="center">

<br/>

**Built with ❤️ for ACM 412 — Django & Web Technologies**

<br/>

[![GitHub](https://img.shields.io/badge/GitHub-behadogangun-181717?style=flat-square&logo=github&logoColor=white)](https://github.com/behadogangun)

<br/>

</div>