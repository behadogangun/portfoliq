import requests
import os
import yfinance as yf
import math
from django.core.cache import cache

COINGECKO_IDS = {
    'BTC': 'bitcoin', 'ETH': 'ethereum', 'BNB': 'binancecoin',
    'SOL': 'solana', 'ADA': 'cardano', 'XRP': 'ripple',
    'DOGE': 'dogecoin', 'AVAX': 'avalanche-2', 'DOT': 'polkadot',
    'MATIC': 'matic-network', 'LINK': 'chainlink', 'UNI': 'uniswap',
    'LTC': 'litecoin', 'BCH': 'bitcoin-cash', 'ATOM': 'cosmos',
    'XLM': 'stellar', 'ALGO': 'algorand', 'VET': 'vechain',
    'ICP': 'internet-computer', 'FIL': 'filecoin', 'TRX': 'tron',
    'ETC': 'ethereum-classic', 'XMR': 'monero', 'NEAR': 'near',
    'APT': 'aptos', 'OP': 'optimism', 'ARB': 'arbitrum',
    'SUI': 'sui', 'INJ': 'injective-protocol', 'PEPE': 'pepe',
}
HARDCODED_CRYPTOS = [
    {'id': 'bitcoin', 'symbol': 'BTC', 'name': 'Bitcoin', 'image': 'https://coin-images.coingecko.com/coins/images/1/large/bitcoin.png', 'current_price': 108234.00, 'price_change_percentage_24h': 2.14, 'market_cap': 2143000000000, 'total_volume': 38000000000},
    {'id': 'ethereum', 'symbol': 'ETH', 'name': 'Ethereum', 'image': 'https://coin-images.coingecko.com/coins/images/279/large/ethereum.png', 'current_price': 2543.00, 'price_change_percentage_24h': 1.87, 'market_cap': 306000000000, 'total_volume': 18000000000},
    {'id': 'binancecoin', 'symbol': 'BNB', 'name': 'BNB', 'image': 'https://coin-images.coingecko.com/coins/images/825/large/bnb-icon2_2x.png', 'current_price': 658.00, 'price_change_percentage_24h': 0.54, 'market_cap': 92000000000, 'total_volume': 2100000000},
    {'id': 'solana', 'symbol': 'SOL', 'name': 'Solana', 'image': 'https://coin-images.coingecko.com/coins/images/4128/large/solana.png', 'current_price': 172.00, 'price_change_percentage_24h': 3.21, 'market_cap': 83000000000, 'total_volume': 4200000000},
    {'id': 'ripple', 'symbol': 'XRP', 'name': 'XRP', 'image': 'https://coin-images.coingecko.com/coins/images/44/large/xrp-symbol-white-128.png', 'current_price': 2.34, 'price_change_percentage_24h': 1.43, 'market_cap': 134000000000, 'total_volume': 5600000000},
    {'id': 'cardano', 'symbol': 'ADA', 'name': 'Cardano', 'image': 'https://coin-images.coingecko.com/coins/images/975/large/cardano.png', 'current_price': 0.72, 'price_change_percentage_24h': 0.88, 'market_cap': 25000000000, 'total_volume': 780000000},
    {'id': 'dogecoin', 'symbol': 'DOGE', 'name': 'Dogecoin', 'image': 'https://coin-images.coingecko.com/coins/images/5/large/dogecoin.png', 'current_price': 0.198, 'price_change_percentage_24h': 1.23, 'market_cap': 29000000000, 'total_volume': 1200000000},
    {'id': 'avalanche-2', 'symbol': 'AVAX', 'name': 'Avalanche', 'image': 'https://coin-images.coingecko.com/coins/images/12559/large/Avalanche_Circle_RedWhite_Trans.png', 'current_price': 23.40, 'price_change_percentage_24h': 2.87, 'market_cap': 9800000000, 'total_volume': 450000000},
    {'id': 'polkadot', 'symbol': 'DOT', 'name': 'Polkadot', 'image': 'https://coin-images.coingecko.com/coins/images/12171/large/polkadot.png', 'current_price': 4.82, 'price_change_percentage_24h': 0.34, 'market_cap': 7200000000, 'total_volume': 210000000},
    {'id': 'chainlink', 'symbol': 'LINK', 'name': 'Chainlink', 'image': 'https://coin-images.coingecko.com/coins/images/877/large/chainlink-new-logo.png', 'current_price': 14.20, 'price_change_percentage_24h': 1.56, 'market_cap': 9100000000, 'total_volume': 380000000},
    {'id': 'uniswap', 'symbol': 'UNI', 'name': 'Uniswap', 'image': 'https://coin-images.coingecko.com/coins/images/12504/large/uniswap-uni.png', 'current_price': 6.43, 'price_change_percentage_24h': 0.77, 'market_cap': 3900000000, 'total_volume': 142000000},
    {'id': 'litecoin', 'symbol': 'LTC', 'name': 'Litecoin', 'image': 'https://coin-images.coingecko.com/coins/images/2/large/litecoin.png', 'current_price': 87.30, 'price_change_percentage_24h': 0.43, 'market_cap': 6500000000, 'total_volume': 320000000},
    {'id': 'bitcoin-cash', 'symbol': 'BCH', 'name': 'Bitcoin Cash', 'image': 'https://coin-images.coingecko.com/coins/images/780/large/bitcoin-cash-circle.png', 'current_price': 398.00, 'price_change_percentage_24h': 1.12, 'market_cap': 7900000000, 'total_volume': 290000000},
    {'id': 'near', 'symbol': 'NEAR', 'name': 'NEAR Protocol', 'image': 'https://coin-images.coingecko.com/coins/images/10365/large/near.jpg', 'current_price': 3.12, 'price_change_percentage_24h': 2.34, 'market_cap': 3700000000, 'total_volume': 180000000},
    {'id': 'aptos', 'symbol': 'APT', 'name': 'Aptos', 'image': 'https://coin-images.coingecko.com/coins/images/26455/large/aptos_round.png', 'current_price': 5.43, 'price_change_percentage_24h': 1.87, 'market_cap': 2800000000, 'total_volume': 120000000},
    {'id': 'sui', 'symbol': 'SUI', 'name': 'Sui', 'image': 'https://coin-images.coingecko.com/coins/images/26375/large/sui_asset.jpeg', 'current_price': 3.21, 'price_change_percentage_24h': 4.12, 'market_cap': 10200000000, 'total_volume': 890000000},
    {'id': 'pepe', 'symbol': 'PEPE', 'name': 'Pepe', 'image': 'https://coin-images.coingecko.com/coins/images/29850/large/pepe-token.jpeg', 'current_price': 0.0000132, 'price_change_percentage_24h': 3.45, 'market_cap': 5600000000, 'total_volume': 1200000000},
    {'id': 'tron', 'symbol': 'TRX', 'name': 'TRON', 'image': 'https://coin-images.coingecko.com/coins/images/1094/large/tron-logo.png', 'current_price': 0.267, 'price_change_percentage_24h': 0.21, 'market_cap': 23000000000, 'total_volume': 980000000},
    {'id': 'stellar', 'symbol': 'XLM', 'name': 'Stellar', 'image': 'https://coin-images.coingecko.com/coins/images/100/large/Stellar_symbol_black_RGB.png', 'current_price': 0.287, 'price_change_percentage_24h': 0.87, 'market_cap': 8700000000, 'total_volume': 210000000},
    {'id': 'monero', 'symbol': 'XMR', 'name': 'Monero', 'image': 'https://coin-images.coingecko.com/coins/images/69/large/monero_logo.png', 'current_price': 312.00, 'price_change_percentage_24h': 0.54, 'market_cap': 5700000000, 'total_volume': 98000000},
]
# Hardcoded US Stocks — Perşembe günü fiyatlar güncellenecek
HARDCODED_STOCKS = [
    {'symbol': 'AAPL', 'name': 'Apple Inc.', 'price': 211.45, 'change': 0.54},
    {'symbol': 'MSFT', 'name': 'Microsoft', 'price': 415.60, 'change': -0.71},
    {'symbol': 'NVDA', 'name': 'NVIDIA', 'price': 1087.20, 'change': 1.23},
    {'symbol': 'GOOGL', 'name': 'Alphabet', 'price': 178.90, 'change': 0.31},
    {'symbol': 'AMZN', 'name': 'Amazon', 'price': 196.75, 'change': 0.89},
    {'symbol': 'META', 'name': 'Meta', 'price': 579.30, 'change': -0.21},
    {'symbol': 'TSLA', 'name': 'Tesla', 'price': 178.20, 'change': -1.45},
    {'symbol': 'JPM', 'name': 'JPMorgan Chase', 'price': 234.50, 'change': 0.66},
    {'symbol': 'BAC', 'name': 'Bank of America', 'price': 43.20, 'change': 0.44},
    {'symbol': 'GS', 'name': 'Goldman Sachs', 'price': 502.30, 'change': 1.81},
    {'symbol': 'V', 'name': 'Visa', 'price': 327.80, 'change': -0.32},
    {'symbol': 'MA', 'name': 'Mastercard', 'price': 489.60, 'change': 0.18},
    {'symbol': 'WMT', 'name': 'Walmart', 'price': 94.50, 'change': 0.22},
    {'symbol': 'JNJ', 'name': 'Johnson & Johnson', 'price': 148.30, 'change': -0.15},
    {'symbol': 'XOM', 'name': 'Exxon Mobil', 'price': 112.40, 'change': 0.55},
    {'symbol': 'UNH', 'name': 'UnitedHealth', 'price': 491.20, 'change': 0.33},
    {'symbol': 'LLY', 'name': 'Eli Lilly', 'price': 797.50, 'change': 1.12},
    {'symbol': 'HD', 'name': 'Home Depot', 'price': 342.10, 'change': -0.48},
    {'symbol': 'PG', 'name': 'Procter & Gamble', 'price': 165.80, 'change': 0.11},
    {'symbol': 'NFLX', 'name': 'Netflix', 'price': 628.40, 'change': 2.14},
    {'symbol': 'ORCL', 'name': 'Oracle', 'price': 138.70, 'change': 0.87},
    {'symbol': 'ADBE', 'name': 'Adobe', 'price': 452.30, 'change': -0.63},
    {'symbol': 'CRM', 'name': 'Salesforce', 'price': 278.90, 'change': 0.44},
    {'symbol': 'AMD', 'name': 'AMD', 'price': 163.40, 'change': 1.56},
    {'symbol': 'INTC', 'name': 'Intel', 'price': 29.80, 'change': -0.77},
    {'symbol': 'COIN', 'name': 'Coinbase', 'price': 224.50, 'change': 3.21},
    {'symbol': 'PLTR', 'name': 'Palantir', 'price': 23.40, 'change': 1.87},
    {'symbol': 'UBER', 'name': 'Uber', 'price': 72.30, 'change': 0.54},
    {'symbol': 'ABNB', 'name': 'Airbnb', 'price': 145.60, 'change': -0.32},
    {'symbol': 'SHOP', 'name': 'Shopify', 'price': 68.90, 'change': 1.23},
]

# Hardcoded BIST Stocks
HARDCODED_BIST = [
    {'symbol': 'THYAO', 'name': 'Türk Hava Yolları', 'price': 248.50, 'change': 1.23},
    {'symbol': 'ASELS', 'name': 'Aselsan', 'price': 64.30, 'change': -0.45},
    {'symbol': 'GARAN', 'name': 'Garanti Bankası', 'price': 112.80, 'change': 0.89},
    {'symbol': 'SASA', 'name': 'SASA Polyester', 'price': 87.40, 'change': 2.14},
    {'symbol': 'KCHOL', 'name': 'Koç Holding', 'price': 198.60, 'change': 0.33},
    {'symbol': 'TUPRS', 'name': 'Tüpraş', 'price': 178.90, 'change': -0.67},
    {'symbol': 'EREGL', 'name': 'Ereğli Demir Çelik', 'price': 43.20, 'change': 0.44},
    {'symbol': 'BIMAS', 'name': 'BIM Mağazaları', 'price': 412.30, 'change': 1.11},
    {'symbol': 'FROTO', 'name': 'Ford Otosan', 'price': 892.50, 'change': -0.28},
    {'symbol': 'SAHOL', 'name': 'Sabancı Holding', 'price': 87.60, 'change': 0.76},
    {'symbol': 'AKBNK', 'name': 'Akbank', 'price': 56.30, 'change': 0.54},
    {'symbol': 'ISCTR', 'name': 'İş Bankası', 'price': 14.82, 'change': -0.13},
    {'symbol': 'TCELL', 'name': 'Turkcell', 'price': 87.90, 'change': 0.23},
    {'symbol': 'SISE', 'name': 'Şişecam', 'price': 38.74, 'change': 1.45},
    {'symbol': 'ARCLK', 'name': 'Arçelik', 'price': 112.40, 'change': -0.87},
]

ALPHA_VANTAGE_KEY = os.environ.get('ALPHA_VANTAGE_KEY', 'demo')
NEWS_API_KEY = os.environ.get('NEWS_API_KEY', '')
TWELVE_DATA_KEY = os.environ.get('TWELVE_DATA_KEY', '')


# --- Kripto ---

def get_crypto_price(symbol):
    """
    Fetches live cryptocurrency price from CoinGecko API.
    Args:
        symbol: Crypto symbol (e.g., 'BTC', 'ETH')
    Returns:
        float price in USD, or None if unavailable
    """
    cache_key = f'crypto_price_{symbol.upper()}'
    cached = cache.get(cache_key)
    if cached:
        return cached
    coin_id = COINGECKO_IDS.get(symbol.upper())
    if not coin_id:
        return None
    try:
        url = f'https://api.coingecko.com/api/v3/simple/price?ids={coin_id}&vs_currencies=usd'
        r = requests.get(url, timeout=5)
        price = float(r.json()[coin_id]['usd'])
        cache.set(cache_key, price, 60)
        return price
    except Exception:
        return None


def get_crypto_info(symbol):
    coin_id = COINGECKO_IDS.get(symbol.upper())
    if not coin_id:
        return None
    try:
        url = (
            f'https://api.coingecko.com/api/v3/coins/{coin_id}'
            f'?localization=false&tickers=false&community_data=false'
            f'&developer_data=false&sparkline=true'
        )
        r = requests.get(url, timeout=8)
        data = r.json()
        market = data.get('market_data', {})
        return {
            'symbol': symbol.upper(),
            'name': data.get('name', symbol),
            'logo': data.get('image', {}).get('large', ''),
            'price': market.get('current_price', {}).get('usd', 0),
            'change_24h': market.get('price_change_percentage_24h', 0),
            'market_cap': market.get('market_cap', {}).get('usd', 0),
            'volume_24h': market.get('total_volume', {}).get('usd', 0),
            'sparkline': market.get('sparkline_in_7d', {}).get('price', []),
        }
    except Exception:
        return None


def search_crypto(query):
    try:
        url = f'https://api.coingecko.com/api/v3/search?query={query}'
        r = requests.get(url, timeout=5)
        coins = r.json().get('coins', [])[:6]
        return [{
            'symbol': c['symbol'].upper(),
            'name': c['name'],
            'logo': c.get('large', c.get('thumb', '')),
            'type': 'crypto',
        } for c in coins]
    except Exception:
        return []


# --- Hisse ---

def get_stock_info(symbol):
    """
    Fetches stock information including price and change from Twelve Data API.
    Falls back to yfinance if Twelve Data is unavailable.
    Args:
        symbol: Stock ticker symbol (e.g., 'AAPL', 'TSLA')
    Returns:
        dict with symbol, name, price, change_24h, logo
    """
    cache_key = f'stock_info_{symbol.upper()}'
   
    cached = cache.get(cache_key)
    if cached:
        return cached
    try:
        url = f'https://api.twelvedata.com/quote?symbol={symbol}&apikey={TWELVE_DATA_KEY}'
        r = requests.get(url, timeout=6)
        data = r.json()

        price = float(data.get('close', 0) or data.get('previous_close', 0))
        prev_close = float(data.get('previous_close', price))
        name = data.get('name', symbol)
        change_24h = ((price - prev_close) / prev_close * 100) if prev_close else 0

        if not price:
            raise ValueError('No price')

        result = {
            'symbol': symbol.upper(),
            'name': name,
            'logo': f'https://financialmodelingprep.com/image-stock/{symbol}.png',
            'price': round(price, 2),
            'change_24h': round(change_24h, 2),
            'market_cap': 0,
            'volume_24h': 0,
            'sector': '',
            'sparkline': [],
        }
        cache.set(cache_key, result, 60)
        return result
    except Exception:
        # Fallback: yfinance
        try:
            import yfinance as yf
            info = yf.Ticker(symbol).info
            price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
            prev_close = info.get('previousClose') or price
            change_24h = ((price - prev_close) / prev_close * 100) if prev_close else 0
            result = {
                'symbol': symbol.upper(),
                'name': info.get('longName') or info.get('shortName', symbol),
                'logo': f'https://financialmodelingprep.com/image-stock/{symbol}.png',
                'price': price,
                'change_24h': round(change_24h, 2),
                'market_cap': info.get('marketCap', 0),
                'volume_24h': info.get('volume', 0),
                'sector': info.get('sector', ''),
                'sparkline': [],
            }
            cache.set(cache_key, result, 60)
            return result
        except Exception:
            return None


FMP_KEY = os.environ.get('FMP_KEY', '')

def search_stocks(query):
    # FMP yeni endpoint
    try:
        url = f'https://financialmodelingprep.com/stable/search-symbol?query={query}&apikey={FMP_KEY}'
        r = requests.get(url, timeout=6)
        data = r.json()
        results = []
        for item in data[:6]:
            symbol = item.get('symbol', '')
            name = item.get('name', '') or item.get('companyName', '')
            exchange = item.get('exchangeShortName', '') or item.get('exchange', '')
            if not symbol or not name:
                continue
            if exchange not in ['NASDAQ', 'NYSE', 'NYSE ARCA', 'AMEX']:
                continue
            results.append({
                'symbol': symbol,
                'name': name,
                'logo': f'https://financialmodelingprep.com/image-stock/{symbol}.png',
                'type': 'stock',
            })
        if results:
            return results
    except Exception:
        pass

    # Fallback: Alpha Vantage
    try:
        url = (
            f'https://www.alphavantage.co/query'
            f'?function=SYMBOL_SEARCH&keywords={query}&apikey={ALPHA_VANTAGE_KEY}'
        )
        r = requests.get(url, timeout=5)
        matches = r.json().get('bestMatches', [])[:5]
        results = []
        for m in matches:
            if m.get('4. region') == 'United States':
                symbol = m['1. symbol']
                results.append({
                    'symbol': symbol,
                    'name': m['2. name'],
                    'logo': f'https://financialmodelingprep.com/image-stock/{symbol}.png',
                    'type': 'stock',
                })
        return results
    except Exception:
        return []




# --- Altın & Döviz ---

def get_gold_price():
    try:
        url = (
            f'https://www.alphavantage.co/query'
            f'?function=CURRENCY_EXCHANGE_RATE'
            f'&from_currency=XAU&to_currency=USD&apikey={ALPHA_VANTAGE_KEY}'
        )
        r = requests.get(url, timeout=5)
        price = r.json().get('Realtime Currency Exchange Rate', {}).get('5. Exchange Rate')
        return float(price) if price else None
    except Exception:
        return None


def get_currency_price(symbol):
    try:
        url = (
            f'https://www.alphavantage.co/query'
            f'?function=CURRENCY_EXCHANGE_RATE'
            f'&from_currency=USD&to_currency={symbol}&apikey={ALPHA_VANTAGE_KEY}'
        )
        r = requests.get(url, timeout=5)
        price = r.json().get('Realtime Currency Exchange Rate', {}).get('5. Exchange Rate')
        return float(price) if price else None
    except Exception:
        return None


# --- Ana fetch fonksiyonu ---

def fetch_price(asset):
    symbol = asset.symbol.upper()
    if asset.asset_type == 'crypto':
        return get_crypto_price(symbol)
    elif asset.asset_type == 'stock':
        info = get_stock_info(symbol)
        return info['price'] if info else None
    elif asset.asset_type == 'gold':
        return get_gold_price()
    elif asset.asset_type == 'currency':
        return get_currency_price(symbol)
    return None


def fetch_asset_info(symbol, asset_type):
    if asset_type == 'crypto':
        return get_crypto_info(symbol)
    elif asset_type == 'stock':
        return get_stock_info(symbol)
    return None


# --- Market overview ---

def get_top_cryptos():
    cache_key = 'top_cryptos'
    cached = cache.get(cache_key)
    if cached:
        return cached
    try:
        url = (
            'https://api.coingecko.com/api/v3/coins/markets'
            '?vs_currency=usd&order=market_cap_desc&per_page=20&page=1'
            '&sparkline=true&price_change_percentage=24h'
        )
        r = requests.get(url, timeout=10)
        result = r.json()
        cache.set(cache_key, result, 120)
        return result
    except Exception:
        return []


def get_top_stocks():
    symbols = [
        'AAPL', 'MSFT', 'NVDA', 'AMZN', 'GOOGL',
        'META', 'TSLA', 'BRK-B', 'JPM', 'V',
        'UNH', 'XOM', 'LLY', 'JNJ', 'WMT',
        'MA', 'PG', 'HD', 'MRK', 'ORCL'
    ]
    stocks = []
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
            prev_close = info.get('previousClose') or price
            change_24h = ((price - prev_close) / prev_close * 100) if prev_close else 0
            stocks.append({
                'symbol': symbol,
                'name': info.get('shortName', symbol),
                'image': f'https://financialmodelingprep.com/image-stock/{symbol}.png',
                'current_price': round(price, 2),
                'price_change_percentage_24h': round(change_24h, 2),
                'market_cap': info.get('marketCap', 0),
                'total_volume': info.get('volume', 0),
            })
        except Exception:
            continue
    return stocks


# --- News ---

def get_asset_news(symbol, name):
    if not NEWS_API_KEY:
        return []
    try:
        query = f'{symbol} OR {name} stock'
        url = (
            f'https://newsapi.org/v2/everything'
            f'?q={query}&sortBy=publishedAt&pageSize=5'
            f'&language=en&apiKey={NEWS_API_KEY}'
        )
        r = requests.get(url, timeout=5)
        articles = r.json().get('articles', [])
        return [{
            'title': a.get('title', ''),
            'description': a.get('description', ''),
            'url': a.get('url', ''),
            'source': a.get('source', {}).get('name', ''),
            'published_at': a.get('publishedAt', ''),
            'image': a.get('urlToImage', ''),
        } for a in articles if a.get('title')]
    except Exception:
        return []


def get_market_news():
    if not NEWS_API_KEY:
        return []
    try:
        url = (
            f'https://newsapi.org/v2/everything'
            f'?q=stock market OR cryptocurrency OR Bitcoin OR Tesla OR Apple'
            f'&sortBy=publishedAt&pageSize=20&language=en&apiKey={NEWS_API_KEY}'
        )
        r = requests.get(url, timeout=5)
        articles = r.json().get('articles', [])
        return [{
            'title': a.get('title', ''),
            'description': a.get('description', ''),
            'url': a.get('url', ''),
            'source': a.get('source', {}).get('name', ''),
            'published_at': a.get('publishedAt', ''),
            'image': a.get('urlToImage', ''),
        } for a in articles if a.get('title') and '[Removed]' not in a.get('title', '')]
    except Exception:
        return []


# --- Risk Metrics ---

def calculate_risk_metrics(prices_list):
    
    if len(prices_list) < 2:                
        return None
    """
    Calculates key risk metrics for an asset based on price history.
    Args:
        prices_list: List of historical prices
    Returns:
        dict with sharpe_ratio, volatility, max_drawdown, total_return
    """
    returns = []
    for i in range(1, len(prices_list)):
        if prices_list[i-1] > 0:
            r = (prices_list[i] - prices_list[i-1]) / prices_list[i-1]
            returns.append(r)

    if not returns:
        return None

    n = len(returns)
    mean_return = sum(returns) / n
    variance = sum((r - mean_return) ** 2 for r in returns) / n
    std_dev = math.sqrt(variance)

    risk_free_daily = 0.04 / 252
    sharpe = ((mean_return - risk_free_daily) / std_dev * math.sqrt(252)) if std_dev > 0 else 0
    volatility = std_dev * math.sqrt(252) * 100

    peak = prices_list[0]
    max_drawdown = 0
    for price in prices_list:
        if price > peak:
            peak = price
        drawdown = (peak - price) / peak * 100 if peak > 0 else 0
        if drawdown > max_drawdown:
            max_drawdown = drawdown

    total_return = ((prices_list[-1] - prices_list[0]) / prices_list[0] * 100) if prices_list[0] > 0 else 0

    return {
        'sharpe_ratio': round(sharpe, 2),
        'volatility': round(volatility, 2),
        'max_drawdown': round(max_drawdown, 2),
        'total_return': round(total_return, 2),
        'avg_daily_return': round(mean_return * 100, 4),
    }


# --- Intelligence ---

def get_fear_greed_index():
    cache_key = 'fear_greed_index'
    cached = cache.get(cache_key)
    if cached:
        return cached
    try:
        r = requests.get('https://api.alternative.me/fng/?limit=1', timeout=5)
        data = r.json()['data'][0]
        result = {
            'value': int(data['value']),
            'classification': data['value_classification'],
            'timestamp': data['timestamp'],
        }
        cache.set(cache_key, result, 300)
        return result
    except Exception:
        return {'value': 50, 'classification': 'Neutral', 'timestamp': ''}



def calculate_portfolio_health(portfolios):
    """
    Calculates overall portfolio health score (A-D grade).
    Args:
        portfolios: QuerySet of Portfolio objects
    Returns:
        dict with score, grade, grade_color, and detailed breakdown
    """
    all_assets = []
    for p in portfolios:
        all_assets.extend(list(p.assets.all()))

    if not all_assets:
        return None

    details = []

    asset_count = len(all_assets)
    type_counts = {}
    for a in all_assets:
        type_counts[a.asset_type] = type_counts.get(a.asset_type, 0) + 1
    type_diversity = len(type_counts)

    if asset_count >= 10:
        div_score = 30
    elif asset_count >= 5:
        div_score = 20
    elif asset_count >= 3:
        div_score = 15
    else:
        div_score = 5
    if type_diversity >= 3:
        div_score = min(div_score + 5, 30)

    details.append({'label': 'Diversification', 'score': div_score, 'max': 30,
                    'desc': f'{asset_count} assets across {type_diversity} asset type(s)', 'color': '#0071e3'})

    total_value = sum(a.current_value() for a in all_assets)
    if total_value > 0:
        max_weight = max(a.current_value() / total_value for a in all_assets)
        if max_weight > 0.7:
            conc_score, msg = 5, f'Highest concentration: {max_weight*100:.0f}% — very high risk'
        elif max_weight > 0.5:
            conc_score, msg = 12, f'Highest concentration: {max_weight*100:.0f}% — moderate risk'
        elif max_weight > 0.3:
            conc_score, msg = 20, f'Highest concentration: {max_weight*100:.0f}% — acceptable'
        else:
            conc_score, msg = 25, f'Highest concentration: {max_weight*100:.0f}% — well balanced'
    else:
        conc_score, msg = 25, 'No value data'

    details.append({'label': 'Concentration Risk', 'score': conc_score, 'max': 25,
                    'desc': msg, 'color': '#5856d6'})

    total_cost = sum(a.total_cost() for a in all_assets)
    total_pl_pct = ((total_value - total_cost) / total_cost * 100) if total_cost > 0 else 0
    if total_pl_pct >= 20: prof_score = 25
    elif total_pl_pct >= 10: prof_score = 20
    elif total_pl_pct >= 0: prof_score = 15
    elif total_pl_pct >= -10: prof_score = 8
    else: prof_score = 3

    details.append({'label': 'Profitability', 'score': prof_score, 'max': 25,
                    'desc': f'{total_pl_pct:+.2f}% overall return',
                    'color': '#1c7f3e' if total_pl_pct >= 0 else '#c4162a'})

    risk_score = 20 if len(all_assets) > 1 else 15
    details.append({'label': 'Risk Management', 'score': risk_score, 'max': 20,
                    'desc': f'Portfolio tracked with {len(all_assets)} position(s)', 'color': '#ff9500'})

    total_score = div_score + conc_score + prof_score + risk_score

    if total_score >= 80: grade, grade_color, grade_desc = 'A', '#1c7f3e', 'Excellent'
    elif total_score >= 65: grade, grade_color, grade_desc = 'B', '#0071e3', 'Good'
    elif total_score >= 50: grade, grade_color, grade_desc = 'C', '#ff9500', 'Fair'
    else: grade, grade_color, grade_desc = 'D', '#c4162a', 'Needs Improvement'

    return {'score': total_score, 'grade': grade, 'grade_color': grade_color,
            'grade_desc': grade_desc, 'details': details}


def get_smart_rebalancing(all_assets):
    if not all_assets:
        return []
    total_value = sum(a.current_value() for a in all_assets)
    if total_value == 0:
        return []

    current = {}
    for a in all_assets:
        current[a.asset_type] = current.get(a.asset_type, 0) + a.current_value()

    ideal = {'stock': 0.50, 'crypto': 0.30, 'gold': 0.10, 'currency': 0.05, 'other': 0.05}
    suggestions = []
    for asset_type, target_pct in ideal.items():
        current_val = current.get(asset_type, 0)
        current_pct = current_val / total_value
        diff = (total_value * target_pct) - current_val
        diff_pct = (current_pct - target_pct) * 100
        if abs(diff_pct) > 5:
            suggestions.append({
                'type': asset_type.title(),
                'current_pct': round(current_pct * 100, 1),
                'target_pct': round(target_pct * 100, 1),
                'diff': round(diff, 2),
                'action': 'Buy' if diff > 0 else 'Reduce',
                'action_color': '#1c7f3e' if diff > 0 else '#c4162a',
            })
    return suggestions


# --- Historical Price ---

def get_historical_price(symbol, asset_type, days=365):
    """Geçmiş fiyat verisi çeker."""
    try:
        if asset_type == 'crypto':
            coin_id = COINGECKO_IDS.get(symbol.upper())
            if not coin_id:
                return []
            url = (
                f'https://api.coingecko.com/api/v3/coins/{coin_id}/market_chart'
                f'?vs_currency=usd&days={days}&interval=daily'
            )
            r = requests.get(url, timeout=10)
            prices = r.json().get('prices', [])
            return [{'timestamp': p[0], 'price': p[1]} for p in prices]

        elif asset_type == 'stock':
            if days <= 30:
                period = '1mo'
            elif days <= 90:
                period = '3mo'
            elif days <= 180:
                period = '6mo'
            elif days <= 365:
                period = '1y'
            elif days <= 730:
                period = '2y'
            else:
                period = '5y'

            ticker = yf.Ticker(symbol)
            hist = ticker.history(period=period)
            if hist.empty:
                return []
            return [
                {'timestamp': int(idx.timestamp() * 1000), 'price': float(row['Close'])}
                for idx, row in hist.iterrows()
            ]
    except Exception:
        return []
    

def get_correlation_matrix(assets):
    """Varlıklar arası korelasyon matrisi hesaplar."""
    import math

    # Her varlık için price history çek
    price_data = {}
    for asset in assets:
        prices = list(asset.prices.order_by('timestamp').values_list('price', flat=True))
        if len(prices) >= 5:
            price_data[asset.symbol] = [float(p) for p in prices]

    if len(price_data) < 2:
        return None

    # Günlük getiriler
    returns = {}
    for symbol, prices in price_data.items():
        r = []
        for i in range(1, len(prices)):
            if prices[i-1] > 0:
                r.append((prices[i] - prices[i-1]) / prices[i-1])
        if r:
            returns[symbol] = r

    symbols = list(returns.keys())
    if len(symbols) < 2:
        return None

    # Min uzunluğa kırp
    min_len = min(len(returns[s]) for s in symbols)
    for s in symbols:
        returns[s] = returns[s][-min_len:]

    def pearson(x, y):
        n = len(x)
        if n == 0:
            return 0
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        num = sum((x[i] - mean_x) * (y[i] - mean_y) for i in range(n))
        den_x = math.sqrt(sum((xi - mean_x) ** 2 for xi in x))
        den_y = math.sqrt(sum((yi - mean_y) ** 2 for yi in y))
        if den_x == 0 or den_y == 0:
            return 0
        return round(num / (den_x * den_y), 2)

    matrix = []
    for s1 in symbols:
        row = []
        for s2 in symbols:
            row.append(pearson(returns[s1], returns[s2]))
        matrix.append(row)

    return {'symbols': symbols, 'matrix': matrix}



def calculate_portfolio_dna(all_assets):
    """
    Portföyü analiz edip yatırım kişiliği çıkarır.
    """
    if not all_assets:
        return None

    total_value = sum(a.current_value() for a in all_assets)
    if total_value == 0:
        return None

    # Varlık tipi dağılımı
    type_values = {}
    for a in all_assets:
        t = a.asset_type
        type_values[t] = type_values.get(t, 0) + a.current_value()

    crypto_pct = type_values.get('crypto', 0) / total_value * 100
    stock_pct = type_values.get('stock', 0) / total_value * 100
    gold_pct = type_values.get('gold', 0) / total_value * 100

    # Ortalama P&L
    all_pl = [a.profit_loss_percent() for a in all_assets if a.total_cost() > 0]
    avg_pl = sum(all_pl) / len(all_pl) if all_pl else 0

    # Risk skoru (0-100)
    risk_score = 0
    risk_score += min(crypto_pct * 0.7, 50)   # Kripto = yüksek risk
    risk_score += min(stock_pct * 0.3, 30)     # Hisse = orta risk
    risk_score += min(gold_pct * 0.1, 10)      # Altın = düşük risk
    risk_score = min(round(risk_score), 100)

    # Kişilik belirleme
    if crypto_pct >= 70:
        personality = 'Crypto Maximalist'
        emoji = '🚀'
        color = '#ff9500'
        desc = 'You live and breathe crypto. High risk, high reward is your motto.'
        traits = ['High risk tolerance', 'Believes in decentralization', 'Volatile portfolio', 'Long-term hodler']
    elif stock_pct >= 70:
        personality = 'Stock Market Pro'
        emoji = '📊'
        color = '#0071e3'
        desc = 'You trust in the power of the stock market and corporate growth.'
        traits = ['Moderate risk tolerance', 'Believes in fundamentals', 'Diversified holdings', 'Growth-oriented']
    elif gold_pct >= 40:
        personality = 'Safe Haven Seeker'
        emoji = '🥇'
        color = '#b36200'
        desc = 'You value stability and protection against inflation above all.'
        traits = ['Low risk tolerance', 'Inflation-conscious', 'Store of value focus', 'Conservative approach']
    elif crypto_pct >= 30 and stock_pct >= 30:
        personality = 'Balanced Innovator'
        emoji = '⚖️'
        color = '#5856d6'
        desc = 'You blend traditional finance with the new digital economy.'
        traits = ['Balanced risk profile', 'Open to innovation', 'Diversified approach', 'Best of both worlds']
    elif avg_pl > 20:
        personality = 'Alpha Hunter'
        emoji = '🎯'
        color = '#1c7f3e'
        desc = 'You consistently seek above-market returns with calculated risks.'
        traits = ['High conviction bets', 'Performance-driven', 'Active management', 'Return maximizer']
    elif avg_pl < -10:
        personality = 'Diamond Hands'
        emoji = '💎'
        color = '#c4162a'
        desc = "You hold through the storms. HODL is not just a word, it's a lifestyle."
        traits = ['Extreme patience', 'Contrarian mindset', 'Long time horizon', 'Believes in recovery']
    else:
        personality = 'Cautious Strategist'
        emoji = '🧠'
        color = '#6e6e73'
        desc = 'You approach investing with careful analysis and measured steps.'
        traits = ['Analytical mindset', 'Risk-aware', 'Steady approach', 'Consistent returns']

    # DNA traits skorları
    dna_traits = [
        {
            'label': 'Risk Appetite',
            'value': risk_score,
            'left': 'Conservative',
            'right': 'Aggressive',
            'color': '#ff9500' if risk_score > 60 else '#0071e3',
        },
        {
            'label': 'Crypto Exposure',
            'value': round(crypto_pct),
            'left': 'Traditional',
            'right': 'Crypto-native',
            'color': '#ff9500',
        },
        {
            'label': 'Diversification',
            'value': min(len(all_assets) * 10, 100),
            'left': 'Concentrated',
            'right': 'Diversified',
            'color': '#1c7f3e',
        },
        {
            'label': 'Performance',
            'value': min(max(int(avg_pl + 50), 0), 100),
            'left': 'Underwater',
            'right': 'Outperforming',
            'color': '#1c7f3e' if avg_pl >= 0 else '#c4162a',
        },
    ]

    return {
        'personality': personality,
        'emoji': emoji,
        'color': color,
        'desc': desc,
        'traits': traits,
        'dna_traits': dna_traits,
        'risk_score': risk_score,
        'crypto_pct': round(crypto_pct, 1),
        'stock_pct': round(stock_pct, 1),
        'gold_pct': round(gold_pct, 1),
        'avg_pl': round(avg_pl, 2),
        'asset_count': len(all_assets),
    }


def get_dividend_info(symbol):
    """yfinance ile temettü bilgisi çeker."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        dividends = ticker.dividends

        annual_dividend = info.get('dividendRate', 0) or 0
        dividend_yield = info.get('dividendYield', 0) or 0
        payout_ratio = info.get('payoutRatio', 0) or 0
        ex_date = info.get('exDividendDate', None)
        price = info.get('currentPrice') or info.get('regularMarketPrice') or 0

        # Son 8 temettü ödemesi
        recent_dividends = []
        if not dividends.empty:
            recent = dividends.tail(8)
            for date, amount in recent.items():
                recent_dividends.append({
                    'date': date.strftime('%d %b %Y'),
                    'amount': round(float(amount), 4),
                })
            recent_dividends.reverse()

        return {
            'symbol': symbol,
            'annual_dividend': round(annual_dividend, 2),
            'dividend_yield': round(dividend_yield * 100, 2) if dividend_yield else 0,
            'payout_ratio': round(payout_ratio * 100, 1) if payout_ratio else 0,
            'ex_date': ex_date,
            'price': price,
            'recent_dividends': recent_dividends,
        }
    except Exception:
        return None
    

def calculate_portfolio_beta(all_assets):
    """
    Portföyün piyasaya göre beta katsayısını hesaplar.
    Beta > 1: Piyasadan daha volatil
    Beta < 1: Piyasadan daha stabil
    Beta = 1: Piyasa ile aynı hareket
    """
    import yfinance as yf
    import numpy as np

    try:
        # S&P 500 benchmark olarak al
        spy = yf.Ticker('SPY')
        spy_hist = spy.history(period='1y')['Close']
        spy_returns = spy_hist.pct_change().dropna()

        if len(spy_returns) < 30:
            return None

        asset_betas = []
        portfolio_weights = []
        total_value = sum(a.current_value() for a in all_assets if a.asset_type == 'stock')

        for asset in all_assets:
            if asset.asset_type != 'stock':
                continue
            try:
                ticker = yf.Ticker(asset.symbol)
                hist = ticker.history(period='1y')['Close']
                asset_returns = hist.pct_change().dropna()

                # Ortak tarihleri bul
                common = spy_returns.index.intersection(asset_returns.index)
                if len(common) < 30:
                    continue

                spy_r = spy_returns[common].values
                asset_r = asset_returns[common].values

                covariance = np.cov(asset_r, spy_r)[0][1]
                variance = np.var(spy_r)
                beta = covariance / variance if variance > 0 else 1.0

                weight = asset.current_value() / total_value if total_value > 0 else 0

                asset_betas.append({
                    'symbol': asset.symbol,
                    'name': asset.name,
                    'beta': round(beta, 3),
                    'weight': round(weight * 100, 1),
                    'interpretation': (
                        'Very aggressive' if beta > 1.5 else
                        'Aggressive' if beta > 1.2 else
                        'Moderate' if beta > 0.8 else
                        'Defensive' if beta > 0.5 else
                        'Very defensive'
                    ),
                    'color': (
                        '#c4162a' if beta > 1.5 else
                        '#ff9500' if beta > 1.2 else
                        '#0071e3' if beta > 0.8 else
                        '#1c7f3e' if beta > 0.5 else
                        '#5856d6'
                    ),
                })
                portfolio_weights.append((beta, weight))
            except Exception:
                continue

        if not asset_betas:
            return None

        # Ağırlıklı ortalama beta
        weighted_beta = sum(b * w for b, w in portfolio_weights)
        total_weight = sum(w for _, w in portfolio_weights)
        portfolio_beta = weighted_beta / total_weight if total_weight > 0 else 1.0

        return {
            'portfolio_beta': round(portfolio_beta, 3),
            'asset_betas': asset_betas,
            'interpretation': (
                'Very aggressive — portfolio moves much more than the market' if portfolio_beta > 1.5 else
                'Aggressive — portfolio amplifies market moves' if portfolio_beta > 1.2 else
                'Moderate — portfolio tracks the market closely' if portfolio_beta > 0.8 else
                'Defensive — portfolio is less volatile than the market' if portfolio_beta > 0.5 else
                'Very defensive — portfolio barely reacts to market moves'
            ),
            'color': (
                '#c4162a' if portfolio_beta > 1.5 else
                '#ff9500' if portfolio_beta > 1.2 else
                '#0071e3' if portfolio_beta > 0.8 else
                '#1c7f3e' if portfolio_beta > 0.5 else
                '#5856d6'
            ),
        }
    except Exception:
        return None
    
def get_sector_rotation():
    """S&P 500 sektörlerinin performansını çeker."""
    import yfinance as yf

    sectors = [
        {'name': 'Technology', 'etf': 'XLK', 'icon': '💻', 'color': '#0071e3'},
        {'name': 'Healthcare', 'etf': 'XLV', 'icon': '🏥', 'color': '#1c7f3e'},
        {'name': 'Financials', 'etf': 'XLF', 'icon': '🏦', 'color': '#ff9500'},
        {'name': 'Energy', 'etf': 'XLE', 'icon': '⚡', 'color': '#c4162a'},
        {'name': 'Consumer Disc.', 'etf': 'XLY', 'icon': '🛍️', 'color': '#5856d6'},
        {'name': 'Industrials', 'etf': 'XLI', 'icon': '🏭', 'color': '#34aadc'},
        {'name': 'Utilities', 'etf': 'XLU', 'icon': '💡', 'color': '#6e6e73'},
        {'name': 'Real Estate', 'etf': 'XLRE', 'icon': '🏘️', 'color': '#b36200'},
        {'name': 'Materials', 'etf': 'XLB', 'icon': '⚗️', 'color': '#5856d6'},
        {'name': 'Comm. Services', 'etf': 'XLC', 'icon': '📡', 'color': '#0071e3'},
        {'name': 'Consumer Staples', 'etf': 'XLP', 'icon': '🛒', 'color': '#1c7f3e'},
    ]

    results = []
    for sector in sectors:
        try:
            ticker = yf.Ticker(sector['etf'])
            info = ticker.info
            hist = ticker.history(period='1mo')['Close']

            price = info.get('regularMarketPrice') or info.get('currentPrice') or 0
            prev_close = info.get('previousClose') or price
            change_1d = ((price - prev_close) / prev_close * 100) if prev_close else 0

            # 1 haftalık ve 1 aylık değişim
            if len(hist) >= 5:
                change_1w = ((hist.iloc[-1] - hist.iloc[-5]) / hist.iloc[-5] * 100)
            else:
                change_1w = 0

            if len(hist) >= 20:
                change_1m = ((hist.iloc[-1] - hist.iloc[0]) / hist.iloc[0] * 100)
            else:
                change_1m = 0

            results.append({
                'name': sector['name'],
                'etf': sector['etf'],
                'icon': sector['icon'],
                'color': sector['color'],
                'price': round(price, 2),
                'change_1d': round(change_1d, 2),
                'change_1w': round(change_1w, 2),
                'change_1m': round(change_1m, 2),
            })
        except Exception:
            continue

    # 1 aylık performansa göre sırala
    results.sort(key=lambda x: x['change_1m'], reverse=True)
    return results


def get_ipo_calendar():
    """Yaklaşan ve son IPO'ları çeker."""
    try:
        url = "https://api.nasdaq.com/api/ipo/calendar"
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
            'Accept': 'application/json',
        }
        r = requests.get(url, headers=headers, timeout=8)
        data = r.json()

        upcoming = []
        recent = []

        # Yaklaşan IPO'lar
        priced = data.get('data', {}).get('upcoming', {}).get('upcomingTable', {}).get('rows', [])
        for ipo in priced[:10]:
            upcoming.append({
                'symbol': ipo.get('proposedTickerSymbol', 'N/A'),
                'name': ipo.get('companyName', 'N/A'),
                'exchange': ipo.get('proposedExchange', 'N/A'),
                'price_range': ipo.get('proposedSharePrice', 'N/A'),
                'shares': ipo.get('sharesOffered', 'N/A'),
                'date': ipo.get('expectedPriceDate', 'N/A'),
            })

        # Son IPO'lar
        filed = data.get('data', {}).get('recent', {}).get('recentTable', {}).get('rows', [])
        for ipo in filed[:10]:
            recent.append({
                'symbol': ipo.get('proposedTickerSymbol', 'N/A'),
                'name': ipo.get('companyName', 'N/A'),
                'exchange': ipo.get('proposedExchange', 'N/A'),
                'price': ipo.get('proposedSharePrice', 'N/A'),
                'date': ipo.get('pricedDate', 'N/A'),
                'shares': ipo.get('sharesOffered', 'N/A'),
            })

        return {'upcoming': upcoming, 'recent': recent}
    except Exception:
        return {'upcoming': [], 'recent': []}
    

def get_insider_trading():
    """SEC EDGAR'dan insider trading verisi çeker."""
    try:
        url = "https://efts.sec.gov/LATEST/search-index?q=%22form+4%22&dateRange=custom&startdt=2026-05-01&enddt=2026-05-26&hits.hits._source=period_of_report,display_names,file_date,form_type"
        headers = {'User-Agent': 'PortfoliQ contact@portfoliq.app'}
        r = requests.get(url, headers=headers, timeout=8)
        data = r.json()

        # openinsider.com'dan çek — daha temiz veri
        url2 = "https://openinsider.com/screener?s=&o=&pl=&ph=&ll=&lh=&fd=30&fdr=&td=0&tdr=&fdlyl=&fdlyh=&daysago=&xp=1&xs=1&vl=&vh=&ocl=&och=&sic1=-1&sicl=100&sich=9999&grp=0&nfl=&nfh=&nil=&nih=&nol=&noh=&v2l=&v2h=&oc2l=&oc2h=&sortcol=0&cnt=20&page=1"

        # openinsider.com scraping yerine yfinance kullan
        import yfinance as yf

        # Büyük insider işlemler — bilinen semboller üzerinden
        symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META', 'TSLA', 'NVDA', 'JPM', 'BAC', 'V']
        trades = []

        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                insider = ticker.insider_transactions
                if insider is not None and not insider.empty:
                    for _, row in insider.head(2).iterrows():
                        shares = row.get('Shares', 0) or 0
                        value = row.get('Value', 0) or 0
                        transaction = row.get('Transaction', '') or ''
                        insider_name = row.get('Insider', '') or ''
                        position = row.get('Position', '') or ''
                        date = row.get('Start Date', '') or ''

                        if not transaction:
                            continue

                        is_buy = 'purchase' in str(transaction).lower() or 'buy' in str(transaction).lower()
                        is_sell = 'sale' in str(transaction).lower() or 'sell' in str(transaction).lower()

                        if not (is_buy or is_sell):
                            continue

                        trades.append({
                            'symbol': symbol,
                            'insider': str(insider_name)[:30],
                            'position': str(position)[:25],
                            'transaction': 'Buy' if is_buy else 'Sell',
                            'shares': int(abs(shares)) if shares else 0,
                            'value': int(abs(value)) if value else 0,
                            'date': str(date)[:10] if date else 'N/A',
                            'is_buy': is_buy,
                        })
            except Exception:
                continue

        # Önce buy'lar, sonra sell'ler, tarihe göre
        trades.sort(key=lambda x: (not x['is_buy'], x['date']), reverse=False)
        return trades[:20]

    except Exception:
        return []
    

def get_price_targets(symbol):
    """yfinance'den analist hedef fiyatları çeker."""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info

        current_price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
        target_high = info.get('targetHighPrice') or 0
        target_low = info.get('targetLowPrice') or 0
        target_mean = info.get('targetMeanPrice') or 0
        target_median = info.get('targetMedianPrice') or 0
        recommendation = info.get('recommendationKey') or 'N/A'
        num_analysts = info.get('numberOfAnalystOpinions') or 0

        if not target_mean:
            return None

        upside = ((target_mean - current_price) / current_price * 100) if current_price else 0

        return {
            'symbol': symbol,
            'current_price': round(current_price, 2),
            'target_high': round(target_high, 2),
            'target_low': round(target_low, 2),
            'target_mean': round(target_mean, 2),
            'target_median': round(target_median, 2),
            'upside': round(upside, 2),
            'recommendation': recommendation.upper().replace('_', ' '),
            'num_analysts': num_analysts,
            'rec_color': (
                '#1c7f3e' if recommendation in ['strong_buy', 'buy'] else
                '#ff9500' if recommendation == 'hold' else
                '#c4162a' if recommendation in ['sell', 'strong_sell'] else
                '#6e6e73'
            ),
        }
    except Exception:
        return None
    


def get_portfolio_volatility(all_assets):
    """Portföyün günlük volatilite geçmişini hesaplar."""
    import yfinance as yf
    import numpy as np

    try:
        stock_assets = [a for a in all_assets if a.asset_type == 'stock']
        if not stock_assets:
            return None

        total_value = sum(a.current_value() for a in stock_assets)
        if total_value == 0:
            return None

        daily_returns = {}
        weights = {}

        for asset in stock_assets:
            try:
                ticker = yf.Ticker(asset.symbol)
                hist = ticker.history(period='3mo')['Close']
                if len(hist) < 10:
                    continue
                returns = hist.pct_change().dropna()
                daily_returns[asset.symbol] = returns
                weights[asset.symbol] = asset.current_value() / total_value
            except Exception:
                continue

        if not daily_returns:
            return None

        # Ortak tarihler
        import pandas as pd
        df = pd.DataFrame(daily_returns)
        df = df.dropna()

        if len(df) < 5:
            return None

        # Ağırlıklı portföy günlük getirisi
        portfolio_returns = sum(df[sym] * weights[sym] for sym in df.columns)

        # 10 günlük rolling volatilite (annualized)
        rolling_vol = portfolio_returns.rolling(10).std() * (252 ** 0.5) * 100
        rolling_vol = rolling_vol.dropna()

        labels = [str(d.strftime('%d %b')) for d in rolling_vol.index]
        values = [float(round(float(v), 2)) for v in rolling_vol.values]

        current_vol = float(round(float(portfolio_returns.std() * (252 ** 0.5) * 100), 2))
        avg_vol = float(round(float(rolling_vol.mean()), 2))
        max_vol = float(round(float(rolling_vol.max()), 2))
        min_vol = float(round(float(rolling_vol.min()), 2))

        vol_label = (
            'Very High' if current_vol > 40 else
            'High' if current_vol > 25 else
            'Moderate' if current_vol > 15 else
            'Low'
        )
        vol_color = (
            '#c4162a' if current_vol > 40 else
            '#ff9500' if current_vol > 25 else
            '#0071e3' if current_vol > 15 else
            '#1c7f3e'
        )

        return {
            'labels': labels,
            'values': values,
            'current_vol': current_vol,
            'avg_vol': avg_vol,
            'max_vol': max_vol,
            'min_vol': min_vol,
            'vol_label': vol_label,
            'vol_color': vol_color,
        }
    except Exception:
        return None
    

def monte_carlo_simulation(all_assets, simulations=500, days=252):
    """Monte Carlo simülasyonu — portföyün gelecekteki olası değerlerini hesaplar."""
    import numpy as np

    try:
        stock_assets = [a for a in all_assets if a.asset_type == 'stock']
        if not stock_assets:
            return None

        total_value = sum(a.current_value() for a in all_assets)
        if total_value == 0:
            return None

        daily_returns = []
        weights = []

        for asset in stock_assets:
            prices = list(asset.prices.order_by('timestamp').values_list('price', flat=True))
            if len(prices) < 10:
                continue
            prices = [float(p) for p in prices]
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            if returns:
                daily_returns.append(returns)
                weights.append(asset.current_value() / total_value)

        if not daily_returns:
            return None

        # Her varlık için mean ve std hesapla
        means = [sum(r) / len(r) for r in daily_returns]
        stds = [
            (sum((x - means[i])**2 for x in daily_returns[i]) / len(daily_returns[i])) ** 0.5
            for i in range(len(daily_returns))
        ]

        # Ağırlıklı portföy mean ve std
        portfolio_mean = sum(m * w for m, w in zip(means, weights))
        portfolio_std = sum(s * w for s, w in zip(stds, weights))

        if portfolio_std == 0:
            return None

        # Simülasyonları çalıştır
        np.random.seed(42)
        simulation_results = []

        for _ in range(simulations):
            daily = np.random.normal(portfolio_mean, portfolio_std, days)
            path = total_value
            for d in daily:
                path *= (1 + d)
            simulation_results.append(round(float(path), 2))

        simulation_results.sort()

        percentile_5 = float(np.percentile(simulation_results, 5))
        percentile_25 = float(np.percentile(simulation_results, 25))
        percentile_50 = float(np.percentile(simulation_results, 50))
        percentile_75 = float(np.percentile(simulation_results, 75))
        percentile_95 = float(np.percentile(simulation_results, 95))

        # Chart için bucket dağılımı
        min_val = min(simulation_results)
        max_val = max(simulation_results)
        bucket_count = 30
        bucket_size = (max_val - min_val) / bucket_count if max_val > min_val else 1
        buckets = [0] * bucket_count
        labels = []

        for val in simulation_results:
            idx = min(int((val - min_val) / bucket_size), bucket_count - 1)
            buckets[idx] += 1

        for i in range(bucket_count):
            labels.append(f'${round(min_val + i * bucket_size / 1000, 0):.0f}K')

        return {
            'total_value': round(total_value, 2),
            'simulations': simulations,
            'days': days,
            'p5': round(percentile_5, 2),
            'p25': round(percentile_25, 2),
            'p50': round(percentile_50, 2),
            'p75': round(percentile_75, 2),
            'p95': round(percentile_95, 2),
            'worst': round(min(simulation_results), 2),
            'best': round(max(simulation_results), 2),
            'labels': labels,
            'buckets': buckets,
            'upside_pct': round((percentile_50 - total_value) / total_value * 100, 2),
            'downside_pct': round((percentile_5 - total_value) / total_value * 100, 2),
        }
    except Exception:
        return None
    
def calculate_efficient_frontier(all_assets, num_portfolios=300):
    """Efficient Frontier — risk/getiri optimizasyonu."""
    import numpy as np

    try:
        stock_assets = [a for a in all_assets if a.asset_type == 'stock']
        if len(stock_assets) < 2:
            return None

        # Her varlık için günlük getiri
        returns_data = {}
        for asset in stock_assets:
            prices = list(asset.prices.order_by('timestamp').values_list('price', flat=True))
            if len(prices) < 10:
                continue
            prices = [float(p) for p in prices]
            returns = [(prices[i] - prices[i-1]) / prices[i-1] for i in range(1, len(prices))]
            if len(returns) >= 5:
                returns_data[asset.symbol] = returns

        if len(returns_data) < 2:
            return None

        symbols = list(returns_data.keys())
        n = len(symbols)

        # Min uzunluğa kırp
        min_len = min(len(returns_data[s]) for s in symbols)
        matrix = [[returns_data[s][i] for i in range(min_len)] for s in symbols]

        # Mean returns (annualized)
        means = [sum(r) / len(r) * 252 for r in matrix]

        # Covariance matrix (annualized)
        def cov(x, y):
            n = len(x)
            mx, my = sum(x)/n, sum(y)/n
            return sum((x[i]-mx)*(y[i]-my) for i in range(n)) / n * 252

        cov_matrix = [[cov(matrix[i], matrix[j]) for j in range(n)] for i in range(n)]

        # Random portföyler oluştur
        np.random.seed(42)
        portfolios = []

        for _ in range(num_portfolios):
            weights = np.random.random(n)
            weights = weights / weights.sum()

            # Beklenen getiri
            port_return = float(sum(means[i] * weights[i] for i in range(n)))

            # Portföy varyansı
            port_var = 0
            for i in range(n):
                for j in range(n):
                    port_var += weights[i] * weights[j] * cov_matrix[i][j]

            port_risk = float(port_var ** 0.5)
            sharpe = (port_return - 0.04) / port_risk if port_risk > 0 else 0

            portfolios.append({
                'return': round(port_return * 100, 2),
                'risk': round(port_risk * 100, 2),
                'sharpe': round(sharpe, 3),
                'weights': {symbols[i]: round(float(weights[i]) * 100, 1) for i in range(n)},
            })

        # En iyi Sharpe oranına sahip portföy
        best = max(portfolios, key=lambda x: x['sharpe'])
        min_risk = min(portfolios, key=lambda x: x['risk'])

        # Mevcut portföy ağırlıkları
        total_value = sum(a.current_value() for a in stock_assets if a.symbol in symbols)
        current_weights = {}
        for asset in stock_assets:
            if asset.symbol in symbols and total_value > 0:
                current_weights[asset.symbol] = round(asset.current_value() / total_value * 100, 1)

        current_return = sum(means[i] * (current_weights.get(symbols[i], 0) / 100) for i in range(n))
        current_var = sum(
            (current_weights.get(symbols[i], 0) / 100) * (current_weights.get(symbols[j], 0) / 100) * cov_matrix[i][j]
            for i in range(n) for j in range(n)
        )
        current_risk = float(current_var ** 0.5)

        return {
            'portfolios': portfolios,
            'best_sharpe': best,
            'min_risk': min_risk,
            'symbols': symbols,
            'current': {
                'return': round(float(current_return) * 100, 2),
                'risk': round(current_risk * 100, 2),
                'weights': current_weights,
            },
            'num_portfolios': num_portfolios,
        }
    except Exception:
        return None
    

def get_tcmb_rate():
    cache_key = 'tcmb_rate'
    cached = cache.get(cache_key)
    if cached:
        return cached
    try:
        ticker = yf.Ticker('USDTRY=X')
        info = ticker.info
        rate = info.get('regularMarketPrice') or info.get('previousClose')
        if rate:
            result = round(float(rate), 4)
            cache.set(cache_key, result, 120)
            return result
        r = requests.get('https://api.exchangerate-api.com/v4/latest/USD', timeout=5)
        data = r.json()
        result = round(data['rates'].get('TRY', 32.0), 4)
        cache.set(cache_key, result, 120)
        return result
    except Exception:
        return None


def get_bist_stock(symbol):
    """BIST hisse bilgisi çeker. Symbol: THYAO (otomatik .IS ekler)"""
    try:
        bist_symbol = f'{symbol.upper()}.IS'
        ticker = yf.Ticker(bist_symbol)
        info = ticker.info

        price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
        prev_close = info.get('previousClose') or price
        change_24h = ((price - prev_close) / prev_close * 100) if prev_close else 0

        if not price:
            return None

        return {
            'symbol': symbol.upper(),
            'bist_symbol': bist_symbol,
            'name': info.get('longName') or info.get('shortName', symbol),
            'price': round(price, 2),
            'change_24h': round(change_24h, 2),
            'market_cap': info.get('marketCap', 0),
            'currency': 'TRY',
            'logo': f'https://financialmodelingprep.com/image-stock/{symbol}.png',
            'type': 'stock',
        }
    except Exception:
        return None


def get_bist_overview():
    """BIST'in önde gelen hisselerini çeker."""
    symbols = [
        'THYAO', 'ASELS', 'GARAN', 'SASA', 'KCHOL',
        'TUPRS', 'EREGL', 'BIMAS', 'FROTO', 'SAHOL',
        'AKBNK', 'ISCTR', 'TCELL', 'SISE', 'ARCLK',
    ]
    results = []
    for symbol in symbols:
        try:
            info = get_bist_stock(symbol)
            if info:
                results.append(info)
        except Exception:
            continue
    return results


def get_economic_calendar():
    """Ekonomik takvim verisi — statik ama kapsamlı."""
    import datetime
    today = datetime.date.today()
    year = today.year
    month = today.month

    flag_map = {
    'US': '🇺🇸', 'EU': '🇪🇺', 'UK': '🇬🇧', 'CN': '🇨🇳',
    'JP': '🇯🇵', 'DE': '🇩🇪', 'FR': '🇫🇷', 'CA': '🇨🇦',
    'AU': '🇦🇺', 'CH': '🇨🇭', 'TR': '🇹🇷', 'IT': '🇮🇹',
    'ES': '🇪🇸', 'KR': '🇰🇷', 'IN': '🇮🇳', 'BR': '🇧🇷',
    'MX': '🇲🇽', 'RU': '🇷🇺', 'ZA': '🇿🇦', 'NZ': '🇳🇿',
    'SG': '🇸🇬', 'HK': '🇭🇰', 'SE': '🇸🇪', 'NO': '🇳🇴',
    'NL': '🇳🇱', 'BE': '🇧🇪', 'AT': '🇦🇹', 'PL': '🇵🇱',
    'PT': '🇵🇹', 'GR': '🇬🇷', 'CZ': '🇨🇿', 'HU': '🇭🇺',
    'DK': '🇩🇰', 'FI': '🇫🇮', 'IE': '🇮🇪', 'SA': '🇸🇦',
    'AE': '🇦🇪', 'IL': '🇮🇱', 'TH': '🇹🇭', 'ID': '🇮🇩',
    'MY': '🇲🇾', 'PH': '🇵🇭', 'VN': '🇻🇳', 'TW': '🇹🇼',
    'AR': '🇦🇷', 'CL': '🇨🇱', 'CO': '🇨🇴', 'NG': '🇳🇬',
    'EG': '🇪🇬', 'PK': '🇵🇰', 'BD': '🇧🇩', 'UA': '🇺🇦',
    'RO': '🇷🇴', 'HR': '🇭🇷', 'RS': '🇷🇸', 'BG': '🇧🇬',
    'SK': '🇸🇰', 'SI': '🇸🇮', 'LT': '🇱🇹', 'LV': '🇱🇻',
    'EE': '🇪🇪', 'LU': '🇱🇺', 'MT': '🇲🇹', 'CY': '🇨🇾',
}

    # Gerçek veri çekmeyi dene
    try:
        from_date = today.strftime('%Y-%m-%d')
        to_date = (today + datetime.timedelta(days=30)).strftime('%Y-%m-%d')
        FINNHUB_KEY = os.environ.get('FINNHUB_KEY', 'demo')
        url = f'https://finnhub.io/api/v1/calendar/economic?from={from_date}&to={to_date}&token={FINNHUB_KEY}'
        r = requests.get(url, timeout=6)
        data = r.json()
        events = []
        for item in data.get('economicCalendar', [])[:40]:
            country = item.get('country', '').upper()
            impact = item.get('impact', 'low')
            events.append({
                'date': item.get('time', '')[:10],
                'event': item.get('event', ''),
                'country': country,
                'flag': flag_map.get(country, '🌐'),
                'actual': item.get('actual', '') or '—',
                'estimate': item.get('estimate', '') or '—',
                'prev': item.get('prev', '') or '—',
                'impact': impact,
                'impact_color': '#c4162a' if impact == 'high' else '#ff9500' if impact == 'medium' else '#6e6e73',
                'impact_emoji': '🔴' if impact == 'high' else '🟡' if impact == 'medium' else '⚪',
            })
        if events:
            return sorted(events, key=lambda x: x['date'])
    except Exception:
        pass

    # Fallback — kapsamlı statik liste
    events = [
        {'date': f'{year}-{month:02d}-01', 'event': 'ISM Manufacturing PMI', 'country': 'US', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-05', 'event': 'Non-Farm Payrolls', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-05', 'event': 'Unemployment Rate', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-07', 'event': 'Trade Balance', 'country': 'CN', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-10', 'event': 'CPI Inflation YoY', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-10', 'event': 'Core CPI MoM', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-12', 'event': 'ECB Interest Rate Decision', 'country': 'EU', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-13', 'event': 'PPI Producer Price Index', 'country': 'US', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-14', 'event': 'Retail Sales MoM', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-15', 'event': 'Industrial Production', 'country': 'US', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-16', 'event': 'Consumer Confidence', 'country': 'UK', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-18', 'event': 'CPI Inflation', 'country': 'UK', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-18', 'event': 'RBA Meeting Minutes', 'country': 'AU', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-20', 'event': 'Fed Interest Rate Decision', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-20', 'event': 'FOMC Press Conference', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-21', 'event': 'Bank of Japan Rate Decision', 'country': 'JP', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-22', 'event': 'GDP Growth Rate QoQ', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-23', 'event': 'Manufacturing PMI Flash', 'country': 'EU', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-24', 'event': 'Durable Goods Orders', 'country': 'US', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-25', 'event': 'PCE Price Index MoM', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-25', 'event': 'Core PCE Price Index', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-26', 'event': 'Ifo Business Climate', 'country': 'DE', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-27', 'event': 'TCMB Interest Rate Decision', 'country': 'TR', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-28', 'event': 'Consumer Confidence Index', 'country': 'US', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-30', 'event': 'Chicago PMI', 'country': 'US', 'impact': 'low'},
    ]

    result = []
    for e in events:
        country = e['country']
        impact = e['impact']
        result.append({
            'date': e['date'],
            'event': e['event'],
            'country': country,
            'flag': flag_map.get(country, '🌐'),
            'actual': '—',
            'estimate': '—',
            'prev': '—',
            'impact': impact,
            'impact_color': '#c4162a' if impact == 'high' else '#ff9500' if impact == 'medium' else '#6e6e73',
            'impact_emoji': '🔴' if impact == 'high' else '🟡' if impact == 'medium' else '⚪',
        })

    return sorted(result, key=lambda x: x['date'])

    # Fallback — önemli sabit ekonomik olaylar
    import datetime
    today = datetime.date.today()
    month = today.month
    year = today.year

    static_events = [
        {'date': f'{year}-{month:02d}-05', 'event': 'Non-Farm Payrolls', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-05', 'event': 'Unemployment Rate', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-07', 'event': 'Trade Balance', 'country': 'CN', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-10', 'event': 'CPI Inflation YoY', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-10', 'event': 'Core CPI MoM', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-11', 'event': 'ECB Rate Decision', 'country': 'EU', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-13', 'event': 'PPI Producer Price Index', 'country': 'US', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-14', 'event': 'Retail Sales MoM', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-15', 'event': 'Industrial Production MoM', 'country': 'US', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-16', 'event': 'GDP Growth Rate QoQ', 'country': 'UK', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-18', 'event': 'CPI Inflation YoY', 'country': 'UK', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-18', 'event': 'Bank of Japan Rate Decision', 'country': 'JP', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-20', 'event': 'Fed Interest Rate Decision', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-20', 'event': 'FOMC Press Conference', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-22', 'event': 'GDP Growth Rate QoQ', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-23', 'event': 'Manufacturing PMI Flash', 'country': 'EU', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-23', 'event': 'Services PMI Flash', 'country': 'US', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-24', 'event': 'Durable Goods Orders MoM', 'country': 'US', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-25', 'event': 'Core PCE Price Index MoM', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-25', 'event': 'PCE Price Index YoY', 'country': 'US', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-27', 'event': 'TCMB Interest Rate Decision', 'country': 'TR', 'impact': 'high'},
        {'date': f'{year}-{month:02d}-28', 'event': 'Consumer Confidence Index', 'country': 'US', 'impact': 'medium'},
        {'date': f'{year}-{month:02d}-30', 'event': 'Chicago PMI', 'country': 'US', 'impact': 'low'},
    ]
    return sorted(static_events, key=lambda x: x['date'])


def get_market_mood():
    """10+ indikatörü birleştirip piyasa ruh halini tek emoji ile gösterir."""
    cache_key = 'market_mood'
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        score = 50  # Başlangıç nötr
        indicators = []

        # 1. Fear & Greed Index
        fg = get_fear_greed_index()
        fg_value = fg['value']
        fg_contribution = (fg_value - 50) * 0.3
        score += fg_contribution
        indicators.append({
            'name': 'Fear & Greed Index',
            'value': f'{fg_value}/100',
            'signal': 'bullish' if fg_value > 60 else 'bearish' if fg_value < 40 else 'neutral',
            'icon': '😱' if fg_value < 25 else '😰' if fg_value < 40 else '😐' if fg_value < 60 else '😊' if fg_value < 75 else '🤑',
        })

        # 2. S&P 500 trend
        try:
            spy = yf.Ticker('SPY')
            hist = spy.history(period='1mo')['Close']
            if len(hist) >= 2:
                spy_change = (hist.iloc[-1] - hist.iloc[0]) / hist.iloc[0] * 100
                score += spy_change * 2
                indicators.append({
                    'name': 'S&P 500 (1 Month)',
                    'value': f'{spy_change:+.1f}%',
                    'signal': 'bullish' if spy_change > 2 else 'bearish' if spy_change < -2 else 'neutral',
                    'icon': '📈' if spy_change > 0 else '📉',
                })
        except Exception:
            pass

        # 3. VIX (Volatility Index)
        try:
            vix = yf.Ticker('^VIX')
            vix_info = vix.info
            vix_price = vix_info.get('regularMarketPrice') or vix_info.get('previousClose') or 20
            vix_contribution = -(vix_price - 20) * 0.5
            score += vix_contribution
            indicators.append({
                'name': 'VIX Volatility',
                'value': f'{vix_price:.1f}',
                'signal': 'bullish' if vix_price < 15 else 'bearish' if vix_price > 25 else 'neutral',
                'icon': '😴' if vix_price < 15 else '😬' if vix_price > 25 else '😐',
            })
        except Exception:
            pass

        # 4. Bitcoin trend
        try:
            btc = yf.Ticker('BTC-USD')
            btc_hist = btc.history(period='1mo')['Close']
            if len(btc_hist) >= 2:
                btc_change = (btc_hist.iloc[-1] - btc_hist.iloc[0]) / btc_hist.iloc[0] * 100
                score += btc_change * 0.5
                indicators.append({
                    'name': 'Bitcoin (1 Month)',
                    'value': f'{btc_change:+.1f}%',
                    'signal': 'bullish' if btc_change > 5 else 'bearish' if btc_change < -5 else 'neutral',
                    'icon': '🚀' if btc_change > 10 else '📈' if btc_change > 0 else '📉',
                })
        except Exception:
            pass

        # 5. Gold trend
        try:
            gold = yf.Ticker('GC=F')
            gold_hist = gold.history(period='1mo')['Close']
            if len(gold_hist) >= 2:
                gold_change = (gold_hist.iloc[-1] - gold_hist.iloc[0]) / gold_hist.iloc[0] * 100
                # Altın yükselirse genellikle risk-off (bearish hisse)
                score -= gold_change * 0.3
                indicators.append({
                    'name': 'Gold (1 Month)',
                    'value': f'{gold_change:+.1f}%',
                    'signal': 'bearish' if gold_change > 3 else 'bullish' if gold_change < -3 else 'neutral',
                    'icon': '🥇',
                })
        except Exception:
            pass

        # 6. USD strength
        try:
            dxy = yf.Ticker('DX-Y.NYB')
            dxy_hist = dxy.history(period='1mo')['Close']
            if len(dxy_hist) >= 2:
                dxy_change = (dxy_hist.iloc[-1] - dxy_hist.iloc[0]) / dxy_hist.iloc[0] * 100
                score -= dxy_change * 0.5
                indicators.append({
                    'name': 'USD Strength (DXY)',
                    'value': f'{dxy_change:+.1f}%',
                    'signal': 'bearish' if dxy_change > 1 else 'bullish' if dxy_change < -1 else 'neutral',
                    'icon': '💵',
                })
        except Exception:
            pass

        # Score'u 0-100 arasına sıkıştır
        score = max(0, min(100, score))

        # Mood belirleme
        if score >= 80:
            mood = 'Extreme Greed'
            emoji = '🤑'
            color = '#1c7f3e'
            desc = 'Markets are extremely optimistic. Consider taking some profits.'
        elif score >= 65:
            mood = 'Greed'
            emoji = '😊'
            color = '#34c759'
            desc = 'Investors are optimistic. Momentum is strong.'
        elif score >= 55:
            mood = 'Slightly Bullish'
            emoji = '🙂'
            color = '#0071e3'
            desc = 'Markets lean positive. Cautious optimism.'
        elif score >= 45:
            mood = 'Neutral'
            emoji = '😐'
            color = '#6e6e73'
            desc = 'Markets are balanced. No strong direction.'
        elif score >= 35:
            mood = 'Slightly Bearish'
            emoji = '😟'
            color = '#ff9500'
            desc = 'Markets lean negative. Caution advised.'
        elif score >= 20:
            mood = 'Fear'
            emoji = '😰'
            color = '#ff453a'
            desc = 'Investors are fearful. Could be a buying opportunity.'
        else:
            mood = 'Extreme Fear'
            emoji = '😱'
            color = '#c4162a'
            desc = 'Panic in the markets. Historically a strong buy signal.'

        result = {
            'score': round(score, 1),
            'mood': mood,
            'emoji': emoji,
            'color': color,
            'desc': desc,
            'indicators': indicators,
        }
        cache.set(cache_key, result, 300)
        return result

    except Exception:
        return {
            'score': 50,
            'mood': 'Neutral',
            'emoji': '😐',
            'color': '#6e6e73',
            'desc': 'Could not calculate market mood.',
            'indicators': [],
        }
    

def get_earnings_calendar():
    """Yaklaşan kazanç açıklamalarını çeker."""
    cache_key = 'earnings_calendar'
    cached = cache.get(cache_key)
    if cached:
        return cached

    try:
        import datetime
        symbols = [
            'AAPL', 'MSFT', 'GOOGL', 'AMZN', 'META',
            'TSLA', 'NVDA', 'JPM', 'BAC', 'V',
            'WMT', 'JNJ', 'XOM', 'PG', 'MA',
            'HD', 'UNH', 'LLY', 'ORCL', 'NFLX',
        ]

        earnings = []
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                earnings_date = info.get('earningsTimestamp') or info.get('earningsTimestampStart')
                if not earnings_date:
                    continue

                import datetime
                date = datetime.datetime.fromtimestamp(earnings_date)
                today = datetime.datetime.now()

                # Sadece gelecek 60 gün
                if date < today or (date - today).days > 60:
                    continue

                eps_estimate = info.get('forwardEps') or 0
                revenue_estimate = info.get('revenueEstimate') or 0
                price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
                pe_ratio = info.get('forwardPE') or 0

                earnings.append({
                    'symbol': symbol,
                    'name': info.get('shortName', symbol),
                    'date': date.strftime('%Y-%m-%d'),
                    'time': 'Before Open' if info.get('earningsCallTimePdtStartTime', '') else 'After Close',
                    'eps_estimate': round(float(eps_estimate), 2) if eps_estimate else None,
                    'price': round(float(price), 2) if price else None,
                    'pe_ratio': round(float(pe_ratio), 1) if pe_ratio else None,
                    'days_away': (date - today).days,
                })
            except Exception:
                continue

        earnings.sort(key=lambda x: x['date'])
        cache.set(cache_key, earnings, 3600)  # 1 saat cache
        return earnings

    except Exception:
        return []
    

def get_short_squeeze_candidates():
    """Yüksek short interest olan hisseleri tespit eder."""
    cache_key = 'short_squeeze'
    cached = cache.get(cache_key)
    if cached:
        return cached

    symbols = [
        'GME', 'AMC', 'BBBY', 'TSLA', 'RIVN', 'LCID',
        'PLTR', 'SOFI', 'HOOD', 'COIN', 'MSTR', 'UPST',
        'BYND', 'SPCE', 'NKLA', 'PLUG', 'FCEL', 'BLNK',
        'CVNA', 'OPEN', 'DKNG', 'RBLX', 'PATH', 'U',
    ]

    results = []
    for symbol in symbols:
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info

            short_ratio = info.get('shortRatio') or 0
            short_percent = info.get('shortPercentOfFloat') or 0
            price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
            prev_close = info.get('previousClose') or price
            change_24h = ((price - prev_close) / prev_close * 100) if prev_close else 0
            volume = info.get('volume') or 0
            avg_volume = info.get('averageVolume') or 1
            volume_ratio = round(volume / avg_volume, 2) if avg_volume else 0

            if short_percent < 0.05:  # %5'ten az short olanları atla
                continue

            short_pct_display = round(short_percent * 100, 1)

            # Squeeze skoru hesapla (0-100)
            squeeze_score = 0
            squeeze_score += min(short_pct_display * 1.5, 50)  # Short % ağırlığı
            squeeze_score += min(short_ratio * 3, 20)           # Days to cover
            squeeze_score += min(volume_ratio * 5, 20)          # Volume spike
            squeeze_score += min(max(change_24h, 0) * 2, 10)   # Price momentum
            squeeze_score = min(round(squeeze_score), 100)

            results.append({
                'symbol': symbol,
                'name': info.get('shortName', symbol),
                'price': round(float(price), 2),
                'change_24h': round(float(change_24h), 2),
                'short_percent': short_pct_display,
                'short_ratio': round(float(short_ratio), 1),
                'volume_ratio': volume_ratio,
                'squeeze_score': squeeze_score,
                'score_color': (
                    '#c4162a' if squeeze_score >= 70 else
                    '#ff9500' if squeeze_score >= 50 else
                    '#0071e3' if squeeze_score >= 30 else
                    '#6e6e73'
                ),
                'score_label': (
                    '🔥 Extreme' if squeeze_score >= 70 else
                    '⚠️ High' if squeeze_score >= 50 else
                    '👀 Moderate' if squeeze_score >= 30 else
                    '💤 Low'
                ),
            })
        except Exception:
            continue

    results.sort(key=lambda x: x['squeeze_score'], reverse=True)
    cache.set(cache_key, results, 1800)  # 30 dakika cache
    return results[:15]


def get_famous_portfolios():
    """Ünlü yatırımcıların portföylerini çeker."""
    cache_key = 'famous_portfolios'
    cached = cache.get(cache_key)
    if cached:
        return cached

    famous = {
        'Warren Buffett': {
            'emoji': '🧙',
            'description': 'Value investing legend. CEO of Berkshire Hathaway.',
            'style': 'Value',
            'holdings': [
                {'symbol': 'AAPL', 'weight': 50.0},
                {'symbol': 'BAC', 'weight': 9.3},
                {'symbol': 'AXP', 'weight': 7.5},
                {'symbol': 'KO', 'weight': 6.8},
                {'symbol': 'CVX', 'weight': 5.2},
                {'symbol': 'OXY', 'weight': 4.9},
                {'symbol': 'MCO', 'weight': 3.1},
                {'symbol': 'KHC', 'weight': 2.8},
            ]
        },
        'Cathie Wood (ARK)': {
            'emoji': '🚀',
            'description': 'Innovation investing. ARK Invest founder.',
            'style': 'Growth/Innovation',
            'holdings': [
                {'symbol': 'TSLA', 'weight': 12.5},
                {'symbol': 'COIN', 'weight': 9.8},
                {'symbol': 'ROKU', 'weight': 8.2},
                {'symbol': 'PATH', 'weight': 7.1},
                {'symbol': 'RBLX', 'weight': 6.4},
                {'symbol': 'DKNG', 'weight': 5.9},
                {'symbol': 'HOOD', 'weight': 5.3},
                {'symbol': 'PLTR', 'weight': 4.8},
            ]
        },
        'Ray Dalio': {
            'emoji': '⚖️',
            'description': 'All Weather Portfolio. Bridgewater founder.',
            'style': 'Macro/Balanced',
            'holdings': [
                {'symbol': 'GLD', 'weight': 15.0},
                {'symbol': 'TLT', 'weight': 40.0},
                {'symbol': 'SPY', 'weight': 30.0},
                {'symbol': 'IEF', 'weight': 15.0},
            ]
        },
        'Michael Burry': {
            'emoji': '🐻',
            'description': 'The Big Short. Scion Asset Management.',
            'style': 'Contrarian/Value',
            'holdings': [
                {'symbol': 'GOOGL', 'weight': 18.5},
                {'symbol': 'META', 'weight': 15.2},
                {'symbol': 'AMZN', 'weight': 12.8},
                {'symbol': 'JD', 'weight': 10.1},
                {'symbol': 'BABA', 'weight': 9.4},
                {'symbol': 'CVS', 'weight': 8.7},
            ]
        },
    }

    results = []
    for name, data in famous.items():
        portfolio_return = 0
        enriched_holdings = []
        total_weight = sum(h['weight'] for h in data['holdings'])

        for holding in data['holdings']:
            try:
                info = get_stock_info(holding['symbol'])
                if info:
                    price = info['price']
                    change = info['change_24h']
                    weight_pct = round(holding['weight'] / total_weight * 100, 1)
                    portfolio_return += (change * weight_pct / 100)
                    enriched_holdings.append({
                        'symbol': holding['symbol'],
                        'weight': weight_pct,
                        'price': price,
                        'change': change,
                    })
            except Exception:
                enriched_holdings.append({
                    'symbol': holding['symbol'],
                    'weight': round(holding['weight'] / total_weight * 100, 1),
                    'price': 0,
                    'change': 0,
                })

        results.append({
            'name': name,
            'emoji': data['emoji'],
            'description': data['description'],
            'style': data['style'],
            'holdings': enriched_holdings,
            'daily_return': round(portfolio_return, 2),
        })

    cache.set(cache_key, results, 3600)
    return results



def crisis_simulator(all_assets, crisis_name):
    """Tarihi kriz senaryolarını portföye uygular."""

    crises = {
        '2008_financial': {
            'name': '2008 Financial Crisis',
            'emoji': '🏦',
            'date': 'Sep 2008 - Mar 2009',
            'description': 'The worst financial crisis since the Great Depression. Lehman Brothers collapsed.',
            'color': '#c4162a',
            'drops': {
                'stock': -56.8,
                'crypto': 0,
                'gold': 5.8,
                'currency': -8.2,
                'other': -40.0,
                # Bireysel hisseler
                'AAPL': -60.2, 'MSFT': -44.1, 'GOOGL': -65.3,
                'AMZN': -45.0, 'JPM': -67.8, 'BAC': -88.5,
                'GS': -78.2, 'C': -94.1, 'WFC': -73.4,
                'XOM': -37.2, 'GE': -80.1,
            }
        },
        '2020_covid': {
            'name': 'COVID-19 Crash',
            'emoji': '🦠',
            'date': 'Feb - Mar 2020',
            'description': 'Global pandemic caused the fastest market crash in history — 34% in 33 days.',
            'color': '#5856d6',
            'drops': {
                'stock': -34.0,
                'crypto': -63.0,
                'gold': -12.0,
                'currency': -5.0,
                'other': -30.0,
                'AAPL': -31.7, 'MSFT': -28.9, 'GOOGL': -30.2,
                'AMZN': -26.0, 'TSLA': -60.0, 'JPM': -45.2,
                'BA': -71.0, 'CCL': -84.0, 'XOM': -55.0,
                'BTC': -63.0, 'ETH': -68.0,
            }
        },
        '2022_crypto_winter': {
            'name': '2022 Crypto Winter',
            'emoji': '❄️',
            'date': 'Nov 2021 - Nov 2022',
            'description': 'Terra/Luna collapse, FTX bankruptcy. Bitcoin fell 77% from all-time high.',
            'color': '#0071e3',
            'drops': {
                'stock': -19.4,
                'crypto': -77.0,
                'gold': -3.2,
                'currency': 8.0,
                'other': -25.0,
                'BTC': -77.0, 'ETH': -80.0, 'BNB': -72.0,
                'SOL': -96.0, 'DOGE': -88.0, 'ADA': -89.0,
                'COIN': -86.0, 'MSTR': -80.0,
                'AAPL': -27.0, 'MSFT': -29.0, 'GOOGL': -39.0,
                'META': -64.0, 'AMZN': -49.0, 'NVDA': -66.0,
            }
        },
        '2000_dotcom': {
            'name': 'Dot-com Bubble',
            'emoji': '💻',
            'date': 'Mar 2000 - Oct 2002',
            'description': 'Tech bubble burst. NASDAQ fell 78%. Many internet companies went to zero.',
            'color': '#ff9500',
            'drops': {
                'stock': -49.1,
                'crypto': 0,
                'gold': 12.4,
                'currency': -5.0,
                'other': -35.0,
                'AAPL': -81.0, 'MSFT': -65.0, 'GOOGL': 0,
                'AMZN': -94.0, 'CSCO': -86.0, 'INTC': -82.0,
                'XOM': 8.0, 'JNJ': 5.0, 'WMT': 12.0,
            }
        },
        '1987_black_monday': {
            'name': 'Black Monday 1987',
            'emoji': '🖤',
            'date': 'October 19, 1987',
            'description': 'Largest single-day percentage drop in stock market history — S&P fell 20% in one day.',
            'color': '#1d1d1f',
            'drops': {
                'stock': -22.6,
                'crypto': 0,
                'gold': -7.0,
                'currency': -5.0,
                'other': -18.0,
            }
        },
    }

    if crisis_name not in crises:
        return None

    crisis = crises[crisis_name]
    drops = crisis['drops']

    total_value = sum(a.current_value() for a in all_assets)
    if total_value == 0:
        return None

    scenario_value = 0
    asset_results = []

    for asset in all_assets:
        current_val = asset.current_value()

        # Önce sembol bazlı bak, sonra asset type
        if asset.symbol in drops:
            drop_pct = drops[asset.symbol]
        else:
            drop_pct = drops.get(asset.asset_type, -30.0)

        new_value = current_val * (1 + drop_pct / 100)
        loss = new_value - current_val
        scenario_value += new_value

        asset_results.append({
            'symbol': asset.symbol,
            'name': asset.name,
            'asset_type': asset.asset_type,
            'current_value': round(current_val, 2),
            'new_value': round(new_value, 2),
            'drop_pct': round(drop_pct, 1),
            'loss': round(loss, 2),
        })

    total_loss = scenario_value - total_value
    total_drop_pct = (total_loss / total_value * 100) if total_value > 0 else 0

    # En çok etkilenen varlıklar
    asset_results.sort(key=lambda x: x['drop_pct'])

    return {
        'crisis': crisis,
        'total_value': round(total_value, 2),
        'scenario_value': round(scenario_value, 2),
        'total_loss': round(total_loss, 2),
        'total_drop_pct': round(total_drop_pct, 2),
        'asset_results': asset_results,
        'worst_asset': asset_results[0] if asset_results else None,
        'best_asset': asset_results[-1] if asset_results else None,
    }