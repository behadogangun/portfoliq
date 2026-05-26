from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.http import JsonResponse, HttpResponse
from django.utils import timezone
from django.db.models import Prefetch, Sum
import csv
import datetime
import requests
from collections import defaultdict
import os
ALPHA_VANTAGE_KEY = os.environ.get('ALPHA_VANTAGE_KEY', 'demo')

from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

from .models import Portfolio, Asset, Transaction, PriceHistory, PriceAlert, WatchlistItem
from .forms import PortfolioForm, AssetForm, TransactionForm
from .services import (
    fetch_price, fetch_asset_info, search_crypto, search_stocks,
    get_top_cryptos, get_top_stocks, get_asset_news, get_stock_info,
    get_market_news, calculate_risk_metrics,
    get_fear_greed_index, calculate_portfolio_health, get_smart_rebalancing,
    get_historical_price, get_correlation_matrix,
    calculate_portfolio_beta,
    get_sector_rotation,
    get_ipo_calendar,
    get_insider_trading,
    get_price_targets,
    get_portfolio_volatility,
    monte_carlo_simulation,
    calculate_efficient_frontier,
    get_tcmb_rate,
    get_bist_stock,
    get_bist_overview,
    get_economic_calendar,
    get_market_mood,
    get_earnings_calendar,
    get_short_squeeze_candidates,
    get_famous_portfolios,
    crisis_simulator,
)


@login_required
def dashboard(request):
    has_portfolios = Portfolio.objects.filter(user=request.user).exists()
    show_onboarding = not request.session.get('onboarding_done', False) and not has_portfolios
    portfolios = Portfolio.objects.filter(
        user=request.user
    ).prefetch_related(
        Prefetch('assets', queryset=Asset.objects.prefetch_related(
            Prefetch('prices', queryset=PriceHistory.objects.order_by('-timestamp'))
        ))
    )

    all_assets = Asset.objects.filter(
        portfolio__user=request.user
    ).select_related('portfolio').prefetch_related(
        Prefetch('prices', queryset=PriceHistory.objects.order_by('-timestamp'))
    )

    total_value = sum(p.total_value() for p in portfolios)
    total_cost = sum(
        sum(a.total_cost() for a in p.assets.all()) for p in portfolios
    )
    total_pl = total_value - total_cost
    total_pl_percent = (total_pl / total_cost * 100) if total_cost > 0 else 0

    assets_with_pl = [(a, a.profit_loss_percent()) for a in all_assets if a.total_cost() > 0]
    assets_with_pl.sort(key=lambda x: x[1], reverse=True)
    best_performers = assets_with_pl[:3]
    worst_performers = assets_with_pl[-3:][::-1] if len(assets_with_pl) >= 3 else []

    thirty_days_ago = timezone.now() - datetime.timedelta(days=30)
    price_history = PriceHistory.objects.filter(
        asset__portfolio__user=request.user,
        timestamp__gte=thirty_days_ago
    ).select_related('asset').order_by('timestamp')

    daily_values = defaultdict(float)
    for ph in price_history:
        day = ph.timestamp.strftime('%d %b')
        daily_values[day] += float(ph.price) * float(ph.asset.quantity)

    context = {
        'portfolios': portfolios,
        'total_value': total_value,
        'total_cost': total_cost,
        'total_pl': total_pl,
        'total_pl_percent': total_pl_percent,
        'all_assets': all_assets,
        'best_performers': best_performers,
        'worst_performers': worst_performers,
        'perf_labels': list(daily_values.keys()),
        'perf_values': list(daily_values.values()),
         'show_onboarding': show_onboarding,
    }
    return render(request, 'portfolio/dashboard.html', context)


# --- Portfolio CRUD ---

@login_required
def portfolio_list(request):
    query = request.GET.get('q', '')
    portfolios = Portfolio.objects.filter(
        user=request.user
    ).prefetch_related('assets')
    if query:
        portfolios = portfolios.filter(name__icontains=query)
    paginator = Paginator(portfolios.order_by('-created_at'), 6)
    portfolios = paginator.get_page(request.GET.get('page'))
    return render(request, 'portfolio/portfolio_list.html', {
        'portfolios': portfolios,
        'query': query
    })


@login_required
def portfolio_create(request):
    if request.method == 'POST':
        form = PortfolioForm(request.POST)
        if form.is_valid():
            portfolio = form.save(commit=False)
            portfolio.user = request.user
            portfolio.save()
            messages.success(request, 'Portfolio created!')
            return redirect('portfolio_detail', pk=portfolio.pk)
    else:
        form = PortfolioForm()
    return render(request, 'portfolio/portfolio_form.html', {
        'form': form,
        'title': 'New Portfolio'
    })


@login_required
def portfolio_detail(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    assets = portfolio.assets.prefetch_related(
        Prefetch('prices', queryset=PriceHistory.objects.order_by('-timestamp'))
    )
    total_cost = sum(a.total_cost() for a in assets)
    total_value = portfolio.total_value()
    total_pl = total_value - total_cost
    total_pl_percent = (total_pl / total_cost * 100) if total_cost > 0 else 0

    return render(request, 'portfolio/portfolio_detail.html', {
        'portfolio': portfolio,
        'assets': assets,
        'total_cost': total_cost,
        'total_value': total_value,
        'total_pl': total_pl,
        'total_pl_percent': total_pl_percent,
    })


@login_required
def portfolio_update(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    if request.method == 'POST':
        form = PortfolioForm(request.POST, instance=portfolio)
        if form.is_valid():
            form.save()
            messages.success(request, 'Portfolio updated!')
            return redirect('portfolio_detail', pk=portfolio.pk)
    else:
        form = PortfolioForm(instance=portfolio)
    return render(request, 'portfolio/portfolio_form.html', {
        'form': form,
        'title': 'Edit Portfolio'
    })


@login_required
def portfolio_delete(request, pk):
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    if request.method == 'POST':
        portfolio.delete()
        messages.success(request, 'Portfolio deleted!')
        return redirect('portfolio_list')
    return render(request, 'portfolio/portfolio_confirm_delete.html', {
        'portfolio': portfolio
    })


# --- Asset CRUD ---

@login_required
def asset_create(request, portfolio_pk):
    portfolio = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)
    if request.method == 'POST':
        symbol = request.POST.get('symbol', '').strip().upper()
        name = request.POST.get('name', '').strip()
        asset_type = request.POST.get('asset_type', '').strip()
        quantity = request.POST.get('quantity', '').strip()
        avg_buy_price = request.POST.get('avg_buy_price', '').strip()
        logo = request.POST.get('logo', '').strip()

        if not all([symbol, name, asset_type, quantity, avg_buy_price]):
            messages.error(request, 'Please fill in all fields.')
            return redirect('asset_create', portfolio_pk=portfolio_pk)

        asset = Asset.objects.create(
            portfolio=portfolio,
            symbol=symbol,
            name=name,
            asset_type=asset_type,
            quantity=quantity,
            avg_buy_price=avg_buy_price,
            logo=logo,
        )
        try:
            price = fetch_price(asset)
            if price:
                PriceHistory.objects.create(asset=asset, price=price)
        except Exception:
            pass
        messages.success(request, f'{symbol} added to portfolio!')
        return redirect('portfolio_detail', pk=portfolio.pk)

    return render(request, 'portfolio/asset_form.html', {'portfolio': portfolio})


@login_required
def asset_delete(request, pk):
    asset = get_object_or_404(
        Asset.objects.select_related('portfolio'),
        pk=pk,
        portfolio__user=request.user
    )
    portfolio_pk = asset.portfolio.pk
    if request.method == 'POST':
        asset.delete()
        messages.success(request, 'Asset deleted!')
        return redirect('portfolio_detail', pk=portfolio_pk)
    return render(request, 'portfolio/asset_confirm_delete.html', {'asset': asset})


@login_required
def asset_detail(request, pk):
    asset = get_object_or_404(
        Asset.objects.select_related('portfolio').prefetch_related(
            Prefetch('prices', queryset=PriceHistory.objects.order_by('timestamp')),
            Prefetch('transactions', queryset=Transaction.objects.order_by('-date'))
        ),
        pk=pk,
        portfolio__user=request.user
    )
    prices = list(asset.prices.all())[:60]
    price_labels = [p.timestamp.strftime('%d %b') for p in prices]
    price_values = [float(p.price) for p in prices]
    news = get_asset_news(asset.symbol, asset.name)
    risk = calculate_risk_metrics(price_values) if len(price_values) >= 2 else None

    return render(request, 'portfolio/asset_detail.html', {
        'asset': asset,
        'transactions': asset.transactions.all(),
        'price_labels': price_labels,
        'price_values': price_values,
        'news': news,
        'risk': risk,
    })


# --- Transaction ---

@login_required
def transaction_create(request, pk):
    asset = get_object_or_404(
        Asset.objects.select_related('portfolio'),
        pk=pk,
        portfolio__user=request.user
    )
    if request.method == 'POST':
        form = TransactionForm(request.POST)
        if form.is_valid():
            transaction = form.save(commit=False)
            transaction.asset = asset
            transaction.save()

            tx_quantity = float(transaction.quantity)
            tx_price = float(transaction.price)

            if transaction.transaction_type == 'buy':
                old_total = float(asset.quantity) * float(asset.avg_buy_price)
                new_quantity = float(asset.quantity) + tx_quantity
                new_avg = (old_total + tx_quantity * tx_price) / new_quantity if new_quantity > 0 else tx_price
                asset.quantity = new_quantity
                asset.avg_buy_price = round(new_avg, 2)
            elif transaction.transaction_type == 'sell':
                asset.quantity = max(float(asset.quantity) - tx_quantity, 0)

            asset.save()
            messages.success(request, 'Transaction saved!')
            return redirect('asset_detail', pk=asset.pk)
    else:
        latest_price = asset.prices.order_by('-timestamp').first()
        initial_price = float(latest_price.price) if latest_price else float(asset.avg_buy_price)
        form = TransactionForm(initial={
            'price': initial_price,
            'date': timezone.now().strftime('%Y-%m-%dT%H:%M'),
        })
    return render(request, 'portfolio/transaction_form.html', {
        'form': form,
        'asset': asset
    })


# --- AJAX ---

@login_required
def refresh_prices(request, portfolio_pk):
    """Refreshes all asset prices via AJAX."""
    portfolio = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)
    updated = []
    for asset in portfolio.assets.all():
        price = fetch_price(asset)
        if price:
            PriceHistory.objects.create(asset=asset, price=price)
            updated.append({
                'id': asset.id,
                'symbol': asset.symbol,
                'price': price,
                'current_value': round(float(asset.quantity) * price, 2),
                'profit_loss_percent': round(
                    ((float(asset.quantity) * price - asset.total_cost()) / asset.total_cost() * 100)
                    if asset.total_cost() > 0 else 0, 2
                ),
            })
    return JsonResponse({'updated': updated})


@login_required
def asset_search(request):
    """AJAX: asset search — stocks önce, kripto sonra."""
    query = request.GET.get('q', '').strip()
    if len(query) < 1:
        return JsonResponse({'results': []})

    stock_results = search_stocks(query)
    crypto_results = search_crypto(query)

    seen = set()
    combined = []
    for r in stock_results + crypto_results:
        key = r['symbol']
        if key not in seen:
            seen.add(key)
            combined.append(r)

    return JsonResponse({'results': combined[:8]})


@login_required
def asset_info(request):
    """AJAX: asset detail info."""
    symbol = request.GET.get('symbol', '').strip()
    asset_type = request.GET.get('type', '').strip()
    if not symbol or not asset_type:
        return JsonResponse({'error': 'Missing parameters'}, status=400)
    
    # Cache'den kontrol et
    from django.core.cache import cache
    cache_key = f'asset_info_{symbol}_{asset_type}'
    cached = cache.get(cache_key)
    if cached:
        return JsonResponse(cached)
    
    info = fetch_asset_info(symbol, asset_type)
    if not info:
        return JsonResponse({'error': 'Not found'}, status=404)
    
    cache.set(cache_key, info, 60)
    return JsonResponse(info)



@login_required
def ticker_data(request):
    from django.core.cache import cache
    import logging
    logger = logging.getLogger(__name__)
    
    TWELVE_DATA_KEY = os.environ.get('TWELVE_DATA_KEY', '')
    results = []

    # Crypto
    try:
        ids = 'bitcoin,ethereum,binancecoin,solana,ripple,cardano,dogecoin,avalanche-2'
        r = requests.get(
            f'https://api.coingecko.com/api/v3/simple/price?ids={ids}&vs_currencies=usd&include_24hr_change=true',
            timeout=8
        )
        data = r.json()
        mapping = {
            'bitcoin': 'BTC', 'ethereum': 'ETH', 'binancecoin': 'BNB',
            'solana': 'SOL', 'ripple': 'XRP', 'cardano': 'ADA',
            'dogecoin': 'DOGE', 'avalanche-2': 'AVAX'
        }
        for coin_id, sym in mapping.items():
            if coin_id in data:
                results.append({
                    'symbol': sym,
                    'price': data[coin_id]['usd'],
                    'change': round(data[coin_id].get('usd_24h_change', 0), 2),
                })
        logger.error(f'CRYPTO OK: {len(results)} items, data keys: {list(data.keys())[:3]}')
    except Exception as e:
        logger.error(f'CRYPTO ERROR: {e}')

    # Stocks
    try:
        stock_symbols = ['AAPL', 'TSLA', 'NVDA', 'MSFT', 'GOOGL']
        symbols_str = ','.join(stock_symbols)
        url = f'https://api.twelvedata.com/price?symbol={symbols_str}&apikey={TWELVE_DATA_KEY}'
        r = requests.get(url, timeout=10)
        data = r.json()
        logger.error(f'STOCKS RAW: {str(data)[:200]}')
        for symbol in stock_symbols:
            if symbol in data and isinstance(data[symbol], dict) and 'price' in data[symbol]:
                results.append({
                    'symbol': symbol,
                    'price': float(data[symbol]['price']),
                    'change': 0,
                })
    except Exception as e:
        logger.error(f'STOCKS ERROR: {e}')

    logger.error(f'TICKER TOTAL: {len(results)} results')
    cache.set('ticker_data', results, 120)
    return JsonResponse({'tickers': results})

# --- Market ---

@login_required
def market(request):
    tab = request.GET.get('tab', 'crypto')
    cryptos = get_top_cryptos() if tab == 'crypto' else []
    stocks = get_top_stocks() if tab == 'stocks' else []
    return render(request, 'portfolio/market.html', {
        'cryptos': cryptos,
        'stocks': stocks,
        'tab': tab,
    })


# --- News ---

@login_required
def news(request):
    articles = get_market_news()
    return render(request, 'portfolio/news.html', {'articles': articles})


# --- Landing ---

def landing(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    mock_assets = [
        {'symbol': 'BTC', 'name': 'Bitcoin', 'logo': 'https://coin-images.coingecko.com/coins/images/1/large/bitcoin.png', 'bg': 'rgba(255,149,0,0.1)', 'color': '#b36200', 'icon': 'BT', 'price': '$97,432', 'value': '$48,716', 'pl': '+42.3%', 'pl_color': '#1c7f3e'},
        {'symbol': 'AAPL', 'name': 'Apple Inc.', 'logo': 'https://financialmodelingprep.com/image-stock/AAPL.png', 'bg': 'rgba(0,113,227,0.1)', 'color': '#0071e3', 'icon': 'AA', 'price': '$212.49', 'value': '$42,498', 'pl': '+18.7%', 'pl_color': '#1c7f3e'},
        {'symbol': 'ETH', 'name': 'Ethereum', 'logo': 'https://coin-images.coingecko.com/coins/images/279/large/ethereum.png', 'bg': 'rgba(88,86,214,0.1)', 'color': '#5856d6', 'icon': 'ET', 'price': '$3,241', 'value': '$19,446', 'pl': '-4.2%', 'pl_color': '#c4162a'},
        {'symbol': 'TSLA', 'name': 'Tesla Inc.', 'logo': 'https://financialmodelingprep.com/image-stock/TSLA.png', 'bg': 'rgba(255,204,0,0.15)', 'color': '#b38600', 'icon': 'TS', 'price': '$248.12', 'value': '$14,172', 'pl': '+12.1%', 'pl_color': '#1c7f3e'},
    ]
    return render(request, 'portfolio/landing.html', {'mock_assets': mock_assets})


# --- Watchlist ---

@login_required
def watchlist(request):
    items = WatchlistItem.objects.filter(user=request.user).order_by('-added_at')
    watchlist_data = []
    for item in items:
        info = fetch_asset_info(item.symbol, item.asset_type)
        watchlist_data.append({
            'item': item,
            'price': info.get('price', 0) if info else 0,
            'change_24h': info.get('change_24h', 0) if info else 0,
            'market_cap': info.get('market_cap', 0) if info else 0,
        })
    return render(request, 'portfolio/watchlist.html', {'watchlist_data': watchlist_data})


@login_required
def watchlist_add(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol', '').strip().upper()
        name = request.POST.get('name', '').strip()
        asset_type = request.POST.get('asset_type', '').strip()
        logo = request.POST.get('logo', '').strip()
        if symbol and name and asset_type:
            WatchlistItem.objects.get_or_create(
                user=request.user,
                symbol=symbol,
                defaults={'name': name, 'asset_type': asset_type, 'logo': logo}
            )
            messages.success(request, f'{symbol} added to watchlist!')
    return redirect('watchlist')


@login_required
def watchlist_remove(request, pk):
    item = get_object_or_404(WatchlistItem, pk=pk, user=request.user)
    item.delete()
    messages.success(request, 'Removed from watchlist.')
    return redirect('watchlist')


# --- Price Alerts ---

@login_required
def alerts(request):
    user_alerts = PriceAlert.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'portfolio/alerts.html', {'alerts': user_alerts})


@login_required
def alert_create(request):
    if request.method == 'POST':
        symbol = request.POST.get('symbol', '').strip().upper()
        name = request.POST.get('name', '').strip()
        asset_type = request.POST.get('asset_type', '').strip()
        logo = request.POST.get('logo', '').strip()
        target_price = request.POST.get('target_price', '').strip()
        alert_type = request.POST.get('alert_type', '').strip()
        if all([symbol, name, asset_type, target_price, alert_type]):
            PriceAlert.objects.create(
                user=request.user,
                symbol=symbol,
                name=name,
                asset_type=asset_type,
                logo=logo,
                target_price=target_price,
                alert_type=alert_type,
            )
            messages.success(request, f'Alert created for {symbol}!')
        return redirect('alerts')
    return render(request, 'portfolio/alert_create.html')


@login_required
def alert_delete(request, pk):
    alert = get_object_or_404(PriceAlert, pk=pk, user=request.user)
    alert.delete()
    messages.success(request, 'Alert deleted.')
    return redirect('alerts')


@login_required
def check_alerts(request):
    """AJAX: Check triggered alerts."""
    user_alerts = PriceAlert.objects.filter(user=request.user, is_triggered=False)
    triggered = []
    for alert in user_alerts:
        info = fetch_asset_info(alert.symbol, alert.asset_type)
        if not info:
            continue
        price = info.get('price', 0)
        if (alert.alert_type == 'above' and price >= float(alert.target_price)) or \
           (alert.alert_type == 'below' and price <= float(alert.target_price)):
            alert.is_triggered = True
            alert.save()
            triggered.append({
                'symbol': alert.symbol,
                'alert_type': alert.alert_type,
                'target_price': float(alert.target_price),
                'current_price': price,
            })
    return JsonResponse({'triggered': triggered})


# --- Export ---

@login_required
def export_csv(request, portfolio_pk):
    portfolio = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{portfolio.name}_export.csv"'

    writer = csv.writer(response)
    writer.writerow(['Symbol', 'Name', 'Type', 'Quantity', 'Avg Buy Price', 'Current Value', 'Total Cost', 'P&L', 'P&L %'])

    assets = portfolio.assets.prefetch_related(
        Prefetch('prices', queryset=PriceHistory.objects.order_by('-timestamp'))
    )
    for asset in assets:
        writer.writerow([
            asset.symbol, asset.name, asset.get_asset_type_display(),
            asset.quantity, asset.avg_buy_price,
            round(asset.current_value(), 2), round(asset.total_cost(), 2),
            round(asset.profit_loss(), 2), round(asset.profit_loss_percent(), 2),
        ])
    writer.writerow([])
    writer.writerow(['Total Value', '', '', '', '', round(portfolio.total_value(), 2), '', '', ''])
    return response


@login_required
def export_pdf(request, portfolio_pk):
    portfolio = get_object_or_404(Portfolio, pk=portfolio_pk, user=request.user)
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{portfolio.name}_report.pdf"'

    doc = SimpleDocTemplate(response, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph(f'Portfolio Report: {portfolio.name}', styles['Title']))
    elements.append(Paragraph('Generated by PortfoliQ', styles['Normal']))
    elements.append(Spacer(1, 20))

    assets = portfolio.assets.prefetch_related(
        Prefetch('prices', queryset=PriceHistory.objects.order_by('-timestamp'))
    )
    total_value = portfolio.total_value()
    total_cost = sum(a.total_cost() for a in assets)

    elements.append(Paragraph('Summary', styles['Heading2']))
    summary_data = [
        ['Total Value', f'${round(total_value, 2):,}'],
        ['Total Cost', f'${round(total_cost, 2):,}'],
        ['Total P&L', f'${round(total_value - total_cost, 2):,}'],
        ['Asset Count', str(portfolio.assets.count())],
    ]
    summary_table = Table(summary_data, colWidths=[200, 200])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#f5f5f7')),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 11),
        ('PADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 20))

    elements.append(Paragraph('Assets', styles['Heading2']))
    data = [['Symbol', 'Name', 'Type', 'Quantity', 'Avg Price', 'Value', 'P&L %']]
    for asset in assets:
        data.append([
            asset.symbol, asset.name[:20], asset.get_asset_type_display(),
            str(asset.quantity), f'${asset.avg_buy_price}',
            f'${round(asset.current_value(), 2):,}',
            f'{round(asset.profit_loss_percent(), 2)}%',
        ])

    table = Table(data, colWidths=[60, 120, 70, 70, 80, 80, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0071e3')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('PADDING', (0, 0), (-1, -1), 6),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9f9f9')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e0e0e0')),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
    ]))
    elements.append(table)
    doc.build(elements)
    return response


# --- Intelligence ---

from .services import (
    fetch_price, fetch_asset_info, search_crypto, search_stocks,
    get_top_cryptos, get_top_stocks, get_asset_news, get_stock_info,
    get_market_news, calculate_risk_metrics,
    get_fear_greed_index, calculate_portfolio_health, get_smart_rebalancing,
    get_historical_price, get_correlation_matrix, calculate_portfolio_dna,
)

@login_required
def intelligence(request):
    portfolios = list(Portfolio.objects.filter(
        user=request.user
    ).prefetch_related(
        Prefetch('assets', queryset=Asset.objects.prefetch_related(
            Prefetch('prices', queryset=PriceHistory.objects.order_by('-timestamp'))
        ))
    ))

    all_assets = list(Asset.objects.filter(
        portfolio__user=request.user
    ).prefetch_related(
        Prefetch('prices', queryset=PriceHistory.objects.order_by('timestamp'))
    ))

    health = calculate_portfolio_health(portfolios)
    fear_greed = get_fear_greed_index()
    rebalancing = get_smart_rebalancing(all_assets)
    correlation = get_correlation_matrix(all_assets)
    dna = calculate_portfolio_dna(all_assets)

    return render(request, 'portfolio/intelligence.html', {
        'health': health,
        'fear_greed': fear_greed,
        'rebalancing': rebalancing,
        'all_assets': all_assets,
        'correlation': correlation,
        'dna': dna,
    })


# --- What-If Simulator ---

@login_required
def whatif(request):
    result = None

    if request.method == 'POST':
        symbol = request.POST.get('symbol', '').strip().upper()
        asset_type = request.POST.get('asset_type', '').strip()
        amount = request.POST.get('amount', '1000').strip()
        days = request.POST.get('days', '365').strip()

        try:
            amount = float(amount)
            days = int(days)
        except ValueError:
            messages.error(request, 'Invalid amount or days.')
            return render(request, 'portfolio/whatif.html', {'result': None})

        if not symbol or not asset_type:
            messages.error(request, 'Please select an asset first.')
            return render(request, 'portfolio/whatif.html', {'result': None})

        prices = get_historical_price(symbol, asset_type, days)
        if prices and len(prices) >= 2:
            start_price = prices[0]['price']
            end_price = prices[-1]['price']
            shares = amount / start_price
            current_value = shares * end_price
            profit = current_value - amount
            profit_pct = (profit / amount) * 100

            step = max(1, len(prices) // 50)
            chart_data = prices[::step]
            chart_labels = []
            chart_values = []
            for p in chart_data:
                dt = datetime.datetime.fromtimestamp(p['timestamp'] / 1000)
                chart_labels.append(dt.strftime('%d %b %y'))
                chart_values.append(round((amount / start_price) * p['price'], 2))

            result = {
                'symbol': symbol,
                'asset_type': asset_type,
                'amount': amount,
                'days': days,
                'start_price': round(start_price, 2),
                'end_price': round(end_price, 2),
                'shares': round(shares, 6),
                'current_value': round(current_value, 2),
                'profit': round(profit, 2),
                'profit_pct': round(profit_pct, 2),
                'chart_labels': chart_labels,
                'chart_values': chart_values,
            }
        else:
            messages.error(request, f'Could not fetch price data for {symbol}. Try a different asset.')

    return render(request, 'portfolio/whatif.html', {'result': result})


# --- Break-Even Calculator ---

@login_required
def breakeven(request):
    all_assets = Asset.objects.filter(
        portfolio__user=request.user
    ).select_related('portfolio').prefetch_related(
        Prefetch('prices', queryset=PriceHistory.objects.order_by('-timestamp'))
    )

    results = []
    for asset in all_assets:
        latest = asset.prices.first()
        current_price = float(latest.price) if latest else float(asset.avg_buy_price)
        avg_cost = float(asset.avg_buy_price)
        quantity = float(asset.quantity)
        total_cost = quantity * avg_cost
        current_value = current_price * quantity
        pl = current_value - total_cost
        pl_pct = ((current_value - total_cost) / total_cost * 100) if total_cost > 0 else 0

        pct_to_breakeven = ((avg_cost - current_price) / current_price * 100) if current_price > 0 else 0

        results.append({
            'asset': asset,
            'current_price': current_price,
            'avg_cost': avg_cost,
            'quantity': quantity,
            'total_cost': total_cost,
            'current_value': current_value,
            'pl': round(pl, 2),
            'pl_pct': round(pl_pct, 2),
            'pct_to_breakeven': round(abs(pct_to_breakeven), 2),
            'is_profit': pl >= 0,
        })

    results.sort(key=lambda x: x['pl_pct'], reverse=True)
    return render(request, 'portfolio/breakeven.html', {'results': results})


@login_required
def regret(request):
    """Regret Calculator — iki varlığı karşılaştır."""
    result = None

    if request.method == 'POST':
        symbol_a = request.POST.get('symbol_a', '').strip().upper()
        type_a = request.POST.get('type_a', '').strip()
        symbol_b = request.POST.get('symbol_b', '').strip().upper()
        type_b = request.POST.get('type_b', '').strip()
        amount = request.POST.get('amount', '1000').strip()
        days = request.POST.get('days', '365').strip()

        try:
            amount = float(amount)
            days = int(days)
        except ValueError:
            messages.error(request, 'Invalid amount or days.')
            return render(request, 'portfolio/regret.html', {'result': None})

        if not all([symbol_a, type_a, symbol_b, type_b]):
            messages.error(request, 'Please select both assets.')
            return render(request, 'portfolio/regret.html', {'result': None})

        prices_a = get_historical_price(symbol_a, type_a, days)
        prices_b = get_historical_price(symbol_b, type_b, days)

        if not prices_a or not prices_b or len(prices_a) < 2 or len(prices_b) < 2:
            messages.error(request, 'Could not fetch price data. Try different assets.')
            return render(request, 'portfolio/regret.html', {'result': None})

        def calc(prices, amt):
            start = prices[0]['price']
            end = prices[-1]['price']
            shares = amt / start
            value = shares * end
            profit = value - amt
            pct = (profit / amt) * 100
            return {
                'start_price': round(start, 2),
                'end_price': round(end, 2),
                'shares': round(shares, 6),
                'value': round(value, 2),
                'profit': round(profit, 2),
                'pct': round(pct, 2),
            }

        a = calc(prices_a, amount)
        b = calc(prices_b, amount)

        # Chart — normalize to $100 başlangıç
        def get_chart_points(prices):
            step = max(1, len(prices) // 60)
            pts = prices[::step]
            base = pts[0]['price']
            labels = []
            values = []
            for p in pts:
                dt = datetime.datetime.fromtimestamp(p['timestamp'] / 1000)
                labels.append(dt.strftime('%d %b %y'))
                values.append(round((p['price'] / base) * amount, 2))
            return labels, values

        labels_a, values_a = get_chart_points(prices_a)
        labels_b, values_b = get_chart_points(prices_b)

        # Ortak labels kullan (A'nın label'larını)
        winner = symbol_a if a['pct'] >= b['pct'] else symbol_b
        winner_pct = max(a['pct'], b['pct'])
        loser_pct = min(a['pct'], b['pct'])
        regret_amount = abs(a['value'] - b['value'])

        result = {
            'symbol_a': symbol_a, 'type_a': type_a,
            'symbol_b': symbol_b, 'type_b': type_b,
            'amount': amount, 'days': days,
            'a': a, 'b': b,
            'winner': winner,
            'winner_pct': winner_pct,
            'loser_pct': loser_pct,
            'regret_amount': round(regret_amount, 2),
            'labels': labels_a,
            'values_a': values_a,
            'values_b': values_b,
        }

    return render(request, 'portfolio/regret.html', {'result': result})



@login_required
def heatmap(request):
    """Market Heatmap — S&P 500 style."""
    import yfinance as yf

    sectors = {
        'Technology': ['AAPL', 'MSFT', 'NVDA', 'GOOGL', 'META', 'ORCL', 'CRM', 'AMD', 'INTC', 'QCOM'],
        'Finance': ['JPM', 'BAC', 'WFC', 'GS', 'MS', 'BLK', 'AXP', 'V', 'MA', 'C'],
        'Healthcare': ['JNJ', 'UNH', 'LLY', 'PFE', 'ABBV', 'MRK', 'TMO', 'ABT', 'DHR', 'BMY'],
        'Consumer': ['AMZN', 'TSLA', 'HD', 'MCD', 'NKE', 'SBUX', 'TGT', 'WMT', 'COST', 'PG'],
        'Energy': ['XOM', 'CVX', 'COP', 'SLB', 'EOG', 'PXD', 'MPC', 'VLO', 'PSX', 'OXY'],
    }

    heatmap_data = []
    for sector, symbols in sectors.items():
        sector_stocks = []
        for symbol in symbols:
            try:
                ticker = yf.Ticker(symbol)
                info = ticker.info
                price = info.get('currentPrice') or info.get('regularMarketPrice') or 0
                prev = info.get('previousClose') or price
                change = ((price - prev) / prev * 100) if prev else 0
                market_cap = info.get('marketCap', 0)
                sector_stocks.append({
                    'symbol': symbol,
                    'name': info.get('shortName', symbol)[:15],
                    'change': round(change, 2),
                    'price': round(price, 2),
                    'market_cap': market_cap,
                })
            except Exception:
                continue
        heatmap_data.append({
            'sector': sector,
            'stocks': sector_stocks,
        })

    return render(request, 'portfolio/heatmap.html', {'heatmap_data': heatmap_data})


@login_required
def portfolio_card(request, pk):
    """Shareable portfolio card."""
    portfolio = get_object_or_404(Portfolio, pk=pk, user=request.user)
    assets = portfolio.assets.prefetch_related(
        Prefetch('prices', queryset=PriceHistory.objects.order_by('-timestamp'))
    )
    total_cost = sum(a.total_cost() for a in assets)
    total_value = portfolio.total_value()
    total_pl = total_value - total_cost
    total_pl_percent = (total_pl / total_cost * 100) if total_cost > 0 else 0

    return render(request, 'portfolio/portfolio_card.html', {
        'portfolio': portfolio,
        'assets': assets,
        'total_cost': total_cost,
        'total_value': total_value,
        'total_pl': total_pl,
        'total_pl_percent': total_pl_percent,
    })


@login_required
def onboarding_done(request):
    """Onboarding tamamlandı — session'a kaydet."""
    if request.method == 'POST':
        request.session['onboarding_done'] = True
    return JsonResponse({'ok': True})


@login_required
def dca_planner(request):
    """Dollar Cost Averaging Planner."""
    result = None

    if request.method == 'POST':
        symbol = request.POST.get('symbol', '').strip().upper()
        asset_type = request.POST.get('asset_type', '').strip()
        monthly_amount = request.POST.get('monthly_amount', '100').strip()
        months = request.POST.get('months', '12').strip()
        expected_return = request.POST.get('expected_return', '10').strip()

        try:
            monthly_amount = float(monthly_amount)
            months = int(months)
            expected_return = float(expected_return) / 100 / 12  # aylık oran
        except ValueError:
            messages.error(request, 'Invalid input.')
            return render(request, 'portfolio/dca_planner.html', {'result': None})

        if not symbol or not asset_type:
            messages.error(request, 'Please select an asset.')
            return render(request, 'portfolio/dca_planner.html', {'result': None})

        # DCA hesaplama
        total_invested = 0
        portfolio_value = 0
        chart_labels = []
        chart_invested = []
        chart_value = []

        for month in range(1, months + 1):
            total_invested += monthly_amount
            portfolio_value = (portfolio_value + monthly_amount) * (1 + expected_return)
            chart_labels.append(f'Month {month}')
            chart_invested.append(round(total_invested, 2))
            chart_value.append(round(portfolio_value, 2))

        total_return = portfolio_value - total_invested
        total_return_pct = (total_return / total_invested * 100) if total_invested > 0 else 0

        result = {
            'symbol': symbol,
            'asset_type': asset_type,
            'monthly_amount': monthly_amount,
            'months': months,
            'total_invested': round(total_invested, 2),
            'final_value': round(portfolio_value, 2),
            'total_return': round(total_return, 2),
            'total_return_pct': round(total_return_pct, 2),
            'chart_labels': chart_labels,
            'chart_invested': chart_invested,
            'chart_value': chart_value,
        }

    return render(request, 'portfolio/dca_planner.html', {'result': result})


from .services import (
    fetch_price, fetch_asset_info, search_crypto, search_stocks,
    get_top_cryptos, get_top_stocks, get_asset_news, get_stock_info,
    get_market_news, calculate_risk_metrics,
    get_fear_greed_index, calculate_portfolio_health, get_smart_rebalancing,
    get_historical_price, get_correlation_matrix, calculate_portfolio_dna,
    get_dividend_info,
)

@login_required
def dividend_tracker(request):
    """Dividend Tracker — portföydeki hisselerin temettülerini göster."""
    all_assets = Asset.objects.filter(
        portfolio__user=request.user,
        asset_type='stock'
    ).select_related('portfolio')

    dividend_data = []
    total_annual_income = 0

    for asset in all_assets:
        info = get_dividend_info(asset.symbol)
        if info and info['annual_dividend'] > 0:
            shares = float(asset.quantity)
            annual_income = shares * info['annual_dividend']
            monthly_income = annual_income / 12
            total_annual_income += annual_income

            dividend_data.append({
                'asset': asset,
                'info': info,
                'shares': shares,
                'annual_income': round(annual_income, 2),
                'monthly_income': round(monthly_income, 2),
            })

    dividend_data.sort(key=lambda x: x['annual_income'], reverse=True)

    return render(request, 'portfolio/dividend_tracker.html', {
        'dividend_data': dividend_data,
        'total_annual_income': round(total_annual_income, 2),
        'total_monthly_income': round(total_annual_income / 12, 2),
    })

@login_required
def portfolio_beta(request):
    """Portfolio Beta — piyasaya göre risk ölçümü."""
    all_assets = list(Asset.objects.filter(
        portfolio__user=request.user,
        asset_type='stock'
    ).prefetch_related(
        Prefetch('prices', queryset=PriceHistory.objects.order_by('-timestamp'))
    ))

    beta_data = calculate_portfolio_beta(all_assets)

    return render(request, 'portfolio/portfolio_beta.html', {
        'beta_data': beta_data,
        'asset_count': len(all_assets),
    })

@login_required
def sector_rotation(request):
    """Sector Rotation Tracker."""
    sectors = get_sector_rotation()
    return render(request, 'portfolio/sector_rotation.html', {'sectors': sectors})


@login_required
def ipo_tracker(request):
    """IPO Tracker."""
    ipo_data = get_ipo_calendar()
    return render(request, 'portfolio/ipo_tracker.html', {'ipo_data': ipo_data})


@login_required
def insider_trading(request):
    """Insider Trading Feed."""
    trades = get_insider_trading()
    return render(request, 'portfolio/insider_trading.html', {'trades': trades})

@login_required
def price_targets(request):
    """Price Target Tracker — analist hedef fiyatları."""
    all_assets = Asset.objects.filter(
        portfolio__user=request.user,
        asset_type='stock'
    ).select_related('portfolio')

    results = []
    for asset in all_assets:
        data = get_price_targets(asset.symbol)
        if data:
            results.append({
                'asset': asset,
                'data': data,
            })

    results.sort(key=lambda x: x['data']['upside'], reverse=True)

    return render(request, 'portfolio/price_targets.html', {
        'results': results,
        'asset_count': len(all_assets),
    })

@login_required
def volatility_chart(request):
    """Portfolio Volatility Chart."""
    all_assets = list(Asset.objects.filter(
        portfolio__user=request.user
    ).prefetch_related(
        Prefetch('prices', queryset=PriceHistory.objects.order_by('-timestamp'))
    ))

    vol_data = get_portfolio_volatility(all_assets)

    return render(request, 'portfolio/volatility_chart.html', {
        'vol_data': vol_data,
    })


@login_required
def portfolio_comparison(request):
    """Portfolio Comparison — iki portföyü karşılaştır."""
    portfolios = Portfolio.objects.filter(user=request.user).prefetch_related(
        Prefetch('assets', queryset=Asset.objects.prefetch_related(
            Prefetch('prices', queryset=PriceHistory.objects.order_by('-timestamp'))
        ))
    )

    portfolio_a = None
    portfolio_b = None
    comparison = None

    if request.method == 'POST':
        id_a = request.POST.get('portfolio_a')
        id_b = request.POST.get('portfolio_b')

        if id_a and id_b and id_a != id_b:
            try:
                portfolio_a = portfolios.get(pk=id_a)
                portfolio_b = portfolios.get(pk=id_b)

                def get_stats(p):
                    assets = list(p.assets.all())
                    total_cost = sum(a.total_cost() for a in assets)
                    total_value = p.total_value()
                    total_pl = total_value - total_cost
                    total_pl_pct = (total_pl / total_cost * 100) if total_cost > 0 else 0
                    best = max(assets, key=lambda a: a.profit_loss_percent(), default=None)
                    worst = min(assets, key=lambda a: a.profit_loss_percent(), default=None)
                    type_dist = {}
                    for a in assets:
                        type_dist[a.asset_type] = type_dist.get(a.asset_type, 0) + a.current_value()
                    return {
                        'portfolio': p,
                        'total_value': round(total_value, 2),
                        'total_cost': round(total_cost, 2),
                        'total_pl': round(total_pl, 2),
                        'total_pl_pct': round(total_pl_pct, 2),
                        'asset_count': len(assets),
                        'best': best,
                        'worst': worst,
                        'type_dist': type_dist,
                    }

                stats_a = get_stats(portfolio_a)
                stats_b = get_stats(portfolio_b)

                comparison = {
                    'a': stats_a,
                    'b': stats_b,
                    'winner': 'a' if stats_a['total_pl_pct'] >= stats_b['total_pl_pct'] else 'b',
                }
            except Portfolio.DoesNotExist:
                messages.error(request, 'Portfolio not found.')

    return render(request, 'portfolio/portfolio_comparison.html', {
        'portfolios': portfolios,
        'comparison': comparison,
        'portfolio_a': portfolio_a,
        'portfolio_b': portfolio_b,
    })

@login_required
def monte_carlo(request):
    """Monte Carlo Simulation."""
    all_assets = list(Asset.objects.filter(
        portfolio__user=request.user
    ).prefetch_related(
        Prefetch('prices', queryset=PriceHistory.objects.order_by('timestamp'))
    ))

    days = int(request.GET.get('days', 252))
    sims = int(request.GET.get('sims', 500))

    result = monte_carlo_simulation(all_assets, simulations=sims, days=days)

    return render(request, 'portfolio/monte_carlo.html', {
        'result': result,
        'days': days,
        'sims': sims,
    })

@login_required
def efficient_frontier(request):
    """Efficient Frontier."""
    all_assets = list(Asset.objects.filter(
        portfolio__user=request.user
    ).prefetch_related(
        Prefetch('prices', queryset=PriceHistory.objects.order_by('timestamp'))
    ))

    result = calculate_efficient_frontier(all_assets)

    return render(request, 'portfolio/efficient_frontier.html', {
        'result': result,
    })

@login_required
def bist_market(request):
    """BIST Market — Borsa İstanbul hisseleri."""
    stocks = get_bist_overview()
    usd_try = get_tcmb_rate()

    # Portföy TL değeri
    all_assets = Asset.objects.filter(
        portfolio__user=request.user
    ).prefetch_related(
        Prefetch('prices', queryset=PriceHistory.objects.order_by('-timestamp'))
    )

    total_usd = sum(
        a.current_value() for a in all_assets
        if a.asset_type in ['stock', 'crypto']
    )
    total_try = round(total_usd * usd_try, 2) if usd_try else None

    return render(request, 'portfolio/bist_market.html', {
        'stocks': stocks,
        'usd_try': usd_try,
        'total_usd': round(total_usd, 2),
        'total_try': total_try,
    })

@login_required
def economic_calendar(request):
    """Economic Calendar."""
    events = get_economic_calendar()
    
    # Impact filter
    impact_filter = request.GET.get('impact', 'all')
    if impact_filter != 'all':
        events = [e for e in events if e['impact'] == impact_filter]

    return render(request, 'portfolio/economic_calendar.html', {
        'events': events,
        'impact_filter': impact_filter,
    })

@login_required
def market_mood(request):
    """Market Mood Ring."""
    mood = get_market_mood()
    return render(request, 'portfolio/market_mood.html', {'mood': mood})


@login_required
def earnings_calendar(request):
    """Earnings Calendar."""
    earnings = get_earnings_calendar()
    return render(request, 'portfolio/earnings_calendar.html', {'earnings': earnings})

@login_required
def short_squeeze(request):
    """Short Squeeze Detector."""
    candidates = get_short_squeeze_candidates()
    return render(request, 'portfolio/short_squeeze.html', {'candidates': candidates})

@login_required
def famous_investors(request):
    """Portfolio vs Famous Investors."""
    famous = get_famous_portfolios()

    # Kullanıcı portföyü
    all_assets = Asset.objects.filter(
        portfolio__user=request.user
    ).prefetch_related(
        Prefetch('prices', queryset=PriceHistory.objects.order_by('-timestamp'))
    )

    total_value = sum(a.current_value() for a in all_assets)
    total_cost = sum(a.total_cost() for a in all_assets)
    user_return = round((total_value - total_cost) / total_cost * 100, 2) if total_cost > 0 else 0

    # Günlük getiri hesapla
    user_daily = 0
    for asset in all_assets:
        if total_value > 0:
            weight = asset.current_value() / total_value
            latest = asset.prices.first()
            if latest:
                user_daily += asset.profit_loss_percent() * weight / 100

    return render(request, 'portfolio/famous_investors.html', {
        'famous': famous,
        'user_return': user_return,
        'user_daily': round(user_daily * 100, 2),
        'total_value': round(total_value, 2),
    })


@login_required
def crisis_sim(request):
    """Crisis Simulator."""
    all_assets = list(Asset.objects.filter(
        portfolio__user=request.user
    ).prefetch_related(
        Prefetch('prices', queryset=PriceHistory.objects.order_by('-timestamp'))
    ))

    crisis_name = request.GET.get('crisis', '2008_financial')
    result = crisis_simulator(all_assets, crisis_name)

    crises = [
        {'key': '2008_financial', 'name': '2008 Financial Crisis', 'emoji': '🏦'},
        {'key': '2020_covid', 'name': 'COVID-19 Crash', 'emoji': '🦠'},
        {'key': '2022_crypto_winter', 'name': '2022 Crypto Winter', 'emoji': '❄️'},
        {'key': '2000_dotcom', 'name': 'Dot-com Bubble', 'emoji': '💻'},
        {'key': '1987_black_monday', 'name': 'Black Monday 1987', 'emoji': '🖤'},
    ]

    return render(request, 'portfolio/crisis_sim.html', {
        'result': result,
        'crises': crises,
        'selected': crisis_name,
    })


import os
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def fetch_prices_cron(request):
    """GitHub Actions cron job trigger."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    secret = os.environ.get('FETCH_SECRET', '')
    import json
    try:
        body = json.loads(request.body)
        if body.get('secret') != secret:
            return JsonResponse({'error': 'Unauthorized'}, status=401)
    except Exception:
        return JsonResponse({'error': 'Invalid body'}, status=400)
    
    from .models import Asset, PriceHistory
    from .services import fetch_price
    
    assets = Asset.objects.all()
    updated = 0
    for asset in assets:
        try:
            price = fetch_price(asset)
            if price:
                PriceHistory.objects.create(asset=asset, price=price)
                updated += 1
        except Exception:
            continue
    
    return JsonResponse({'updated': updated, 'total': assets.count()})