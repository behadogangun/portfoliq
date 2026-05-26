from django.test import TestCase, Client
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Portfolio, Asset, Transaction, PriceHistory, PriceAlert, WatchlistItem
from .services import calculate_risk_metrics, calculate_risk_metrics, calculate_portfolio_health, calculate_portfolio_dna, get_smart_rebalancing, get_correlation_matrix
from decimal import Decimal
import json


# ─── Model Tests ───────────────────────────────────────────────

class PortfolioModelTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.portfolio = Portfolio.objects.create(
            user=self.user, name='Test Portfolio', description='Test description'
        )
        self.asset = Asset.objects.create(
            portfolio=self.portfolio, symbol='BTC', name='Bitcoin',
            asset_type='crypto', quantity=Decimal('1.0'), avg_buy_price=Decimal('50000.00')
        )

    def test_portfolio_str(self):
        self.assertEqual(str(self.portfolio), 'testuser - Test Portfolio')

    def test_asset_str(self):
        self.assertIn('BTC', str(self.asset))

    def test_asset_total_cost(self):
        self.assertEqual(self.asset.total_cost(), 50000.0)

    def test_asset_current_value_no_price(self):
        self.assertEqual(self.asset.current_value(), self.asset.total_cost())

    def test_asset_current_value_with_price(self):
        PriceHistory.objects.create(asset=self.asset, price=Decimal('60000.00'))
        self.assertEqual(self.asset.current_value(), 60000.0)

    def test_asset_profit_loss(self):
        PriceHistory.objects.create(asset=self.asset, price=Decimal('60000.00'))
        self.assertEqual(self.asset.profit_loss(), 10000.0)

    def test_asset_profit_loss_percent(self):
        PriceHistory.objects.create(asset=self.asset, price=Decimal('60000.00'))
        self.assertAlmostEqual(self.asset.profit_loss_percent(), 20.0)

    def test_portfolio_total_value(self):
        PriceHistory.objects.create(asset=self.asset, price=Decimal('60000.00'))
        self.assertEqual(self.portfolio.total_value(), 60000.0)

    def test_portfolio_total_value_no_assets(self):
        empty_portfolio = Portfolio.objects.create(user=self.user, name='Empty')
        self.assertEqual(empty_portfolio.total_value(), 0)

    def test_asset_profit_loss_negative(self):
        PriceHistory.objects.create(asset=self.asset, price=Decimal('40000.00'))
        self.assertEqual(self.asset.profit_loss(), -10000.0)

    def test_asset_profit_loss_percent_negative(self):
        PriceHistory.objects.create(asset=self.asset, price=Decimal('40000.00'))
        self.assertAlmostEqual(self.asset.profit_loss_percent(), -20.0)

    def test_multiple_assets_total_value(self):
        asset2 = Asset.objects.create(
            portfolio=self.portfolio, symbol='ETH', name='Ethereum',
            asset_type='crypto', quantity=Decimal('2.0'), avg_buy_price=Decimal('2000.00')
        )
        PriceHistory.objects.create(asset=self.asset, price=Decimal('60000.00'))
        PriceHistory.objects.create(asset=asset2, price=Decimal('3000.00'))
        self.assertEqual(self.portfolio.total_value(), 66000.0)

    def test_transaction_str(self):
        tx = Transaction.objects.create(
            asset=self.asset, transaction_type='buy',
            quantity=Decimal('0.5'), price=Decimal('50000'),
            date='2024-01-01 00:00:00'
        )
        self.assertIn('BTC', str(tx))

    def test_price_history_ordering(self):
        PriceHistory.objects.create(asset=self.asset, price=Decimal('50000'))
        PriceHistory.objects.create(asset=self.asset, price=Decimal('60000'))
        latest = self.asset.prices.first()
        self.assertEqual(float(latest.price), 60000.0)

    def test_asset_quantity_is_decimal(self):
        self.assertIsInstance(self.asset.quantity, Decimal)

    def test_portfolio_created_at_exists(self):
        self.assertIsNotNone(self.portfolio.created_at)

    def test_asset_with_zero_cost(self):
        asset = Asset.objects.create(
            portfolio=self.portfolio, symbol='FREE', name='Free Token',
            asset_type='crypto', quantity=Decimal('100'), avg_buy_price=Decimal('0')
        )
        self.assertEqual(asset.total_cost(), 0)


# ─── Portfolio View Tests ───────────────────────────────────────

class PortfolioViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.portfolio = Portfolio.objects.create(user=self.user, name='Test Portfolio')
        self.asset = Asset.objects.create(
            portfolio=self.portfolio, symbol='AAPL', name='Apple Inc.',
            asset_type='stock', quantity=Decimal('10'), avg_buy_price=Decimal('150.00')
        )

    def test_dashboard_redirect_if_not_logged_in(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_logged_in(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_portfolio_list(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('portfolio_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Portfolio')

    def test_portfolio_list_search(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('portfolio_list') + '?q=Test')
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Portfolio')

    def test_portfolio_list_search_no_results(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('portfolio_list') + '?q=nonexistent')
        self.assertEqual(response.status_code, 200)
        self.assertNotContains(response, 'Test Portfolio')

    def test_portfolio_create(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(reverse('portfolio_create'), {
            'name': 'New Portfolio', 'description': 'Description'
        })
        self.assertEqual(Portfolio.objects.filter(user=self.user).count(), 2)

    def test_portfolio_detail(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('portfolio_detail', kwargs={'pk': self.portfolio.pk}))
        self.assertEqual(response.status_code, 200)

    def test_portfolio_update(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(reverse('portfolio_update', kwargs={'pk': self.portfolio.pk}), {
            'name': 'Updated Portfolio', 'description': 'Updated'
        })
        self.portfolio.refresh_from_db()
        self.assertEqual(self.portfolio.name, 'Updated Portfolio')

    def test_portfolio_delete(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(reverse('portfolio_delete', kwargs={'pk': self.portfolio.pk}))
        self.assertEqual(Portfolio.objects.filter(user=self.user).count(), 0)

    def test_other_user_cannot_access_portfolio(self):
        other = User.objects.create_user(username='other', password='testpass123')
        self.client.login(username='other', password='testpass123')
        response = self.client.get(reverse('portfolio_detail', kwargs={'pk': self.portfolio.pk}))
        self.assertEqual(response.status_code, 404)

    def test_other_user_cannot_delete_portfolio(self):
        other = User.objects.create_user(username='other', password='testpass123')
        self.client.login(username='other', password='testpass123')
        self.client.post(reverse('portfolio_delete', kwargs={'pk': self.portfolio.pk}))
        self.assertTrue(Portfolio.objects.filter(pk=self.portfolio.pk).exists())

    def test_asset_detail(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('asset_detail', kwargs={'pk': self.asset.pk}))
        self.assertEqual(response.status_code, 200)

    def test_asset_delete(self):
        self.client.login(username='testuser', password='testpass123')
        self.client.post(reverse('asset_delete', kwargs={'pk': self.asset.pk}))
        self.assertEqual(Asset.objects.filter(portfolio=self.portfolio).count(), 0)

    def test_portfolio_detail_contains_asset(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('portfolio_detail', kwargs={'pk': self.portfolio.pk}))
        self.assertContains(response, 'AAPL')

    def test_portfolio_create_requires_auth(self):
        response = self.client.get(reverse('portfolio_create'))
        self.assertEqual(response.status_code, 302)

    def test_portfolio_update_requires_auth(self):
        response = self.client.get(reverse('portfolio_update', kwargs={'pk': self.portfolio.pk}))
        self.assertEqual(response.status_code, 302)

    def test_portfolio_delete_requires_auth(self):
        response = self.client.get(reverse('portfolio_delete', kwargs={'pk': self.portfolio.pk}))
        self.assertEqual(response.status_code, 302)

    def test_dashboard_context_has_portfolios(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertIn('portfolios', response.context)

    def test_dashboard_context_has_total_value(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('dashboard'))
        self.assertIn('total_value', response.context)


# ─── Transaction Tests ──────────────────────────────────────────

class TransactionTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.portfolio = Portfolio.objects.create(user=self.user, name='Test')
        self.asset = Asset.objects.create(
            portfolio=self.portfolio, symbol='BTC', name='Bitcoin',
            asset_type='crypto', quantity=Decimal('1.0'), avg_buy_price=Decimal('50000.00')
        )
        self.client.login(username='testuser', password='testpass123')

    def test_transaction_create_buy_updates_quantity(self):
        self.client.post(reverse('transaction_create', kwargs={'pk': self.asset.pk}), {
            'transaction_type': 'buy', 'quantity': '0.5',
            'price': '55000', 'date': '2024-01-01T00:00',
        })
        self.asset.refresh_from_db()
        self.assertAlmostEqual(float(self.asset.quantity), 1.5)

    def test_transaction_create_sell_updates_quantity(self):
        self.client.post(reverse('transaction_create', kwargs={'pk': self.asset.pk}), {
            'transaction_type': 'sell', 'quantity': '0.5',
            'price': '55000', 'date': '2024-01-01T00:00',
        })
        self.asset.refresh_from_db()
        self.assertAlmostEqual(float(self.asset.quantity), 0.5)

    def test_transaction_buy_updates_avg_price(self):
        self.client.post(reverse('transaction_create', kwargs={'pk': self.asset.pk}), {
            'transaction_type': 'buy', 'quantity': '1.0',
            'price': '60000', 'date': '2024-01-01T00:00',
        })
        self.asset.refresh_from_db()
        self.assertAlmostEqual(float(self.asset.avg_buy_price), 55000.0)

    def test_transaction_total_amount(self):
        tx = Transaction.objects.create(
            asset=self.asset, transaction_type='buy',
            quantity=Decimal('2.0'), price=Decimal('30000'),
            date='2024-01-01 00:00:00'
        )
        self.assertEqual(tx.total_amount(), 60000.0)

    def test_transaction_sell_cannot_go_negative(self):
        self.client.post(reverse('transaction_create', kwargs={'pk': self.asset.pk}), {
            'transaction_type': 'sell', 'quantity': '999',
            'price': '50000', 'date': '2024-01-01T00:00',
        })
        self.asset.refresh_from_db()
        self.assertGreaterEqual(float(self.asset.quantity), 0)

    def test_transaction_page_loads(self):
        response = self.client.get(reverse('transaction_create', kwargs={'pk': self.asset.pk}))
        self.assertEqual(response.status_code, 200)


# ─── Auth Tests ─────────────────────────────────────────────────

class AuthViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')

    def test_login_page(self):
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 200)

    def test_login_success(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser', 'password': 'testpass123'
        })
        self.assertEqual(response.status_code, 302)

    def test_login_fail(self):
        response = self.client.post(reverse('login'), {
            'username': 'testuser', 'password': 'wrongpassword'
        })
        self.assertEqual(response.status_code, 200)

    def test_register_page(self):
        response = self.client.get(reverse('register'))
        self.assertEqual(response.status_code, 200)

    def test_register_creates_user(self):
        self.client.post(reverse('register'), {
            'username': 'newuser', 'email': 'new@test.com',
            'password': 'StrongPass123!'
        })
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_logout(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('logout'))
        self.assertEqual(response.status_code, 302)

    def test_authenticated_redirects_from_login(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('login'))
        self.assertEqual(response.status_code, 302)

    def test_profile_page(self):
        self.client.login(username='testuser', password='testpass123')
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 200)

    def test_profile_requires_auth(self):
        response = self.client.get(reverse('profile'))
        self.assertEqual(response.status_code, 302)


# ─── Watchlist Tests ────────────────────────────────────────────

class WatchlistTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_watchlist_page(self):
        response = self.client.get(reverse('watchlist'))
        self.assertEqual(response.status_code, 200)

    def test_watchlist_add(self):
        self.client.post(reverse('watchlist_add'), {
            'symbol': 'BTC', 'name': 'Bitcoin',
            'asset_type': 'crypto', 'logo': ''
        })
        self.assertEqual(WatchlistItem.objects.filter(user=self.user).count(), 1)

    def test_watchlist_add_duplicate(self):
        self.client.post(reverse('watchlist_add'), {
            'symbol': 'BTC', 'name': 'Bitcoin', 'asset_type': 'crypto', 'logo': ''
        })
        self.client.post(reverse('watchlist_add'), {
            'symbol': 'BTC', 'name': 'Bitcoin', 'asset_type': 'crypto', 'logo': ''
        })
        self.assertEqual(WatchlistItem.objects.filter(user=self.user).count(), 1)

    def test_watchlist_remove(self):
        item = WatchlistItem.objects.create(
            user=self.user, symbol='BTC', name='Bitcoin', asset_type='crypto'
        )
        self.client.post(reverse('watchlist_remove', kwargs={'pk': item.pk}))
        self.assertEqual(WatchlistItem.objects.filter(user=self.user).count(), 0)

    def test_watchlist_other_user_cannot_remove(self):
        item = WatchlistItem.objects.create(
            user=self.user, symbol='BTC', name='Bitcoin', asset_type='crypto'
        )
        other = User.objects.create_user(username='other', password='testpass123')
        self.client.login(username='other', password='testpass123')
        self.client.post(reverse('watchlist_remove', kwargs={'pk': item.pk}))
        self.assertEqual(WatchlistItem.objects.filter(user=self.user).count(), 1)

    def test_watchlist_requires_auth(self):
        self.client.logout()
        response = self.client.get(reverse('watchlist'))
        self.assertEqual(response.status_code, 302)


# ─── Price Alert Tests ──────────────────────────────────────────

class PriceAlertTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_alerts_page(self):
        response = self.client.get(reverse('alerts'))
        self.assertEqual(response.status_code, 200)

    def test_alert_create(self):
        self.client.post(reverse('alert_create'), {
            'symbol': 'BTC', 'name': 'Bitcoin', 'asset_type': 'crypto',
            'logo': '', 'target_price': '100000', 'alert_type': 'above'
        })
        self.assertEqual(PriceAlert.objects.filter(user=self.user).count(), 1)

    def test_alert_delete(self):
        alert = PriceAlert.objects.create(
            user=self.user, symbol='BTC', name='Bitcoin',
            asset_type='crypto', target_price=Decimal('100000'), alert_type='above'
        )
        self.client.post(reverse('alert_delete', kwargs={'pk': alert.pk}))
        self.assertEqual(PriceAlert.objects.filter(user=self.user).count(), 0)

    def test_alert_str(self):
        alert = PriceAlert.objects.create(
            user=self.user, symbol='BTC', name='Bitcoin',
            asset_type='crypto', target_price=Decimal('100000'), alert_type='above'
        )
        self.assertIn('BTC', str(alert))

    def test_alert_default_not_triggered(self):
        alert = PriceAlert.objects.create(
            user=self.user, symbol='BTC', name='Bitcoin',
            asset_type='crypto', target_price=Decimal('100000'), alert_type='above'
        )
        self.assertFalse(alert.is_triggered)

    def test_alert_below_type(self):
        self.client.post(reverse('alert_create'), {
            'symbol': 'ETH', 'name': 'Ethereum', 'asset_type': 'crypto',
            'logo': '', 'target_price': '1000', 'alert_type': 'below'
        })
        alert = PriceAlert.objects.get(user=self.user, symbol='ETH')
        self.assertEqual(alert.alert_type, 'below')

    def test_alert_other_user_cannot_delete(self):
        alert = PriceAlert.objects.create(
            user=self.user, symbol='BTC', name='Bitcoin',
            asset_type='crypto', target_price=Decimal('100000'), alert_type='above'
        )
        other = User.objects.create_user(username='other', password='testpass123')
        self.client.login(username='other', password='testpass123')
        self.client.post(reverse('alert_delete', kwargs={'pk': alert.pk}))
        self.assertEqual(PriceAlert.objects.filter(user=self.user).count(), 1)


# ─── Risk Analysis Tests ────────────────────────────────────────

class RiskMetricsTest(TestCase):
    def test_calculate_risk_metrics_basic(self):
        prices = [100, 110, 105, 115, 120, 112, 125]
        result = calculate_risk_metrics(prices)
        self.assertIsNotNone(result)
        self.assertIn('sharpe_ratio', result)
        self.assertIn('volatility', result)
        self.assertIn('max_drawdown', result)
        self.assertIn('total_return', result)

    def test_calculate_risk_metrics_insufficient_data(self):
        result = calculate_risk_metrics([100])
        self.assertIsNone(result)

    def test_calculate_risk_metrics_empty(self):
        result = calculate_risk_metrics([])
        self.assertIsNone(result)

    def test_calculate_risk_metrics_positive_return(self):
        prices = [100, 110, 120, 130, 140]
        result = calculate_risk_metrics(prices)
        self.assertGreater(result['total_return'], 0)

    def test_calculate_risk_metrics_negative_return(self):
        prices = [140, 130, 120, 110, 100]
        result = calculate_risk_metrics(prices)
        self.assertLess(result['total_return'], 0)

    def test_max_drawdown_calculation(self):
        prices = [100, 120, 80, 90]
        result = calculate_risk_metrics(prices)
        self.assertGreater(result['max_drawdown'], 0)

    def test_sharpe_ratio_is_float(self):
        prices = [100, 105, 103, 108, 112]
        result = calculate_risk_metrics(prices)
        self.assertIsInstance(result['sharpe_ratio'], float)

    def test_volatility_is_positive(self):
        prices = [100, 105, 103, 108, 112]
        result = calculate_risk_metrics(prices)
        self.assertGreater(result['volatility'], 0)


# ─── AJAX Tests ─────────────────────────────────────────────────

class AjaxTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_asset_search_empty_query(self):
        response = self.client.get(reverse('asset_search') + '?q=')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['results'], [])

    def test_asset_info_missing_params(self):
        response = self.client.get(reverse('asset_info'))
        self.assertEqual(response.status_code, 400)

    def test_check_alerts_returns_json(self):
        response = self.client.get(reverse('check_alerts'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('triggered', data)

    def test_refresh_prices_requires_auth(self):
        self.client.logout()
        portfolio = Portfolio.objects.create(user=self.user, name='Test')
        response = self.client.get(reverse('refresh_prices', kwargs={'portfolio_pk': portfolio.pk}))
        self.assertEqual(response.status_code, 302)

    def test_asset_search_requires_auth(self):
        self.client.logout()
        response = self.client.get(reverse('asset_search') + '?q=BTC')
        self.assertEqual(response.status_code, 302)

    def test_ticker_data_returns_json(self):
        response = self.client.get(reverse('ticker_data'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertIn('tickers', data)

    def test_ticker_data_requires_auth(self):
        self.client.logout()
        response = self.client.get(reverse('ticker_data'))
        self.assertEqual(response.status_code, 302)


# ─── Export Tests ───────────────────────────────────────────────

class ExportTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.portfolio = Portfolio.objects.create(user=self.user, name='Test Portfolio')
        Asset.objects.create(
            portfolio=self.portfolio, symbol='AAPL', name='Apple Inc.',
            asset_type='stock', quantity=Decimal('5'), avg_buy_price=Decimal('200.00')
        )
        self.client.login(username='testuser', password='testpass123')

    def test_export_csv(self):
        response = self.client.get(
            reverse('export_csv', kwargs={'portfolio_pk': self.portfolio.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'text/csv')
        self.assertIn('AAPL', response.content.decode())

    def test_export_pdf(self):
        response = self.client.get(
            reverse('export_pdf', kwargs={'portfolio_pk': self.portfolio.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response['Content-Type'], 'application/pdf')

    def test_export_other_user_denied(self):
        other = User.objects.create_user(username='other', password='testpass123')
        self.client.login(username='other', password='testpass123')
        response = self.client.get(
            reverse('export_csv', kwargs={'portfolio_pk': self.portfolio.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_export_csv_contains_headers(self):
        response = self.client.get(
            reverse('export_csv', kwargs={'portfolio_pk': self.portfolio.pk})
        )
        content = response.content.decode()
        self.assertIn('Symbol', content)
        self.assertIn('Quantity', content)

    def test_export_pdf_requires_auth(self):
        self.client.logout()
        response = self.client.get(
            reverse('export_pdf', kwargs={'portfolio_pk': self.portfolio.pk})
        )
        self.assertEqual(response.status_code, 302)


# ─── New Feature View Tests ─────────────────────────────────────

class NewFeatureViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.portfolio = Portfolio.objects.create(user=self.user, name='Test Portfolio')
        self.asset = Asset.objects.create(
            portfolio=self.portfolio, symbol='AAPL', name='Apple Inc.',
            asset_type='stock', quantity=Decimal('10'), avg_buy_price=Decimal('150.00')
        )
        self.client.login(username='testuser', password='testpass123')

    def test_intelligence_page_loads(self):
        response = self.client.get(reverse('intelligence'))
        self.assertEqual(response.status_code, 200)

    def test_intelligence_requires_auth(self):
        self.client.logout()
        response = self.client.get(reverse('intelligence'))
        self.assertEqual(response.status_code, 302)

    def test_intelligence_context_has_health(self):
        response = self.client.get(reverse('intelligence'))
        self.assertIn('health', response.context)

    def test_intelligence_context_has_fear_greed(self):
        response = self.client.get(reverse('intelligence'))
        self.assertIn('fear_greed', response.context)

    def test_whatif_page_loads(self):
        response = self.client.get(reverse('whatif'))
        self.assertEqual(response.status_code, 200)

    def test_whatif_requires_auth(self):
        self.client.logout()
        response = self.client.get(reverse('whatif'))
        self.assertEqual(response.status_code, 302)

    def test_whatif_post_missing_asset(self):
        response = self.client.post(reverse('whatif'), {
            'symbol': '', 'asset_type': '', 'amount': '1000', 'days': '365'
        })
        self.assertEqual(response.status_code, 200)

    def test_breakeven_page_loads(self):
        response = self.client.get(reverse('breakeven'))
        self.assertEqual(response.status_code, 200)

    def test_breakeven_requires_auth(self):
        self.client.logout()
        response = self.client.get(reverse('breakeven'))
        self.assertEqual(response.status_code, 302)

    def test_breakeven_context_has_results(self):
        response = self.client.get(reverse('breakeven'))
        self.assertIn('results', response.context)

    def test_regret_page_loads(self):
        response = self.client.get(reverse('regret'))
        self.assertEqual(response.status_code, 200)

    def test_regret_requires_auth(self):
        self.client.logout()
        response = self.client.get(reverse('regret'))
        self.assertEqual(response.status_code, 302)

    def test_news_page_loads(self):
        response = self.client.get(reverse('news'))
        self.assertEqual(response.status_code, 200)

    def test_news_requires_auth(self):
        self.client.logout()
        response = self.client.get(reverse('news'))
        self.assertEqual(response.status_code, 302)

    def test_portfolio_card_loads(self):
        response = self.client.get(
            reverse('portfolio_card', kwargs={'pk': self.portfolio.pk})
        )
        self.assertEqual(response.status_code, 200)

    def test_portfolio_card_other_user_denied(self):
        other = User.objects.create_user(username='other', password='testpass123')
        self.client.login(username='other', password='testpass123')
        response = self.client.get(
            reverse('portfolio_card', kwargs={'pk': self.portfolio.pk})
        )
        self.assertEqual(response.status_code, 404)

    def test_onboarding_done_post(self):
        response = self.client.post(reverse('onboarding_done'))
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.content)
        self.assertEqual(data['ok'], True)

    def test_onboarding_done_requires_auth(self):
        self.client.logout()
        response = self.client.post(reverse('onboarding_done'))
        self.assertEqual(response.status_code, 302)


# ─── Intelligence Service Tests ─────────────────────────────────

class IntelligenceServiceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.portfolio = Portfolio.objects.create(user=self.user, name='Test')

    def _make_asset(self, symbol, asset_type, quantity, avg_price, current_price=None):
        asset = Asset.objects.create(
            portfolio=self.portfolio, symbol=symbol, name=symbol,
            asset_type=asset_type, quantity=Decimal(str(quantity)),
            avg_buy_price=Decimal(str(avg_price))
        )
        if current_price:
            PriceHistory.objects.create(asset=asset, price=Decimal(str(current_price)))
        return asset

    def test_portfolio_health_returns_none_for_empty(self):
        from django.db.models import Prefetch
        portfolios = list(Portfolio.objects.filter(user=self.user).prefetch_related('assets'))
        result = calculate_portfolio_health(portfolios)
        self.assertIsNone(result)

    def test_portfolio_health_returns_grade(self):
        self._make_asset('AAPL', 'stock', 10, 150, 160)
        self._make_asset('BTC', 'crypto', 1, 50000, 55000)
        self._make_asset('ETH', 'crypto', 5, 2000, 2200)
        from django.db.models import Prefetch
        portfolios = list(Portfolio.objects.filter(user=self.user).prefetch_related('assets'))
        result = calculate_portfolio_health(portfolios)
        self.assertIsNotNone(result)
        self.assertIn(result['grade'], ['A', 'B', 'C', 'D'])
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)

    def test_smart_rebalancing_empty(self):
        result = get_smart_rebalancing([])
        self.assertEqual(result, [])

    def test_smart_rebalancing_all_stocks(self):
        assets = [self._make_asset('AAPL', 'stock', 10, 150, 160)]
        result = get_smart_rebalancing(assets)
        self.assertIsInstance(result, list)

    def test_correlation_matrix_needs_two_assets(self):
        asset = self._make_asset('AAPL', 'stock', 10, 150)
        assets = list(Asset.objects.filter(portfolio=self.portfolio).prefetch_related('prices'))
        result = get_correlation_matrix(assets)
        self.assertIsNone(result)

    def test_correlation_matrix_with_two_assets(self):
        for price in [150, 155, 152, 158, 160]:
            a = self._make_asset(f'AAPL{price}', 'stock', 10, 150)
            PriceHistory.objects.create(asset=a, price=Decimal(str(price)))
        assets = list(Asset.objects.filter(portfolio=self.portfolio).prefetch_related('prices'))
        result = get_correlation_matrix(assets)

    def test_portfolio_dna_returns_none_for_empty(self):
        result = calculate_portfolio_dna([])
        self.assertIsNone(result)

    def test_portfolio_dna_stock_heavy(self):
        assets = [self._make_asset('AAPL', 'stock', 100, 150, 160)]
        result = calculate_portfolio_dna(assets)
        self.assertIsNotNone(result)
        self.assertIn('personality', result)
        self.assertIn('emoji', result)
        self.assertIn('traits', result)

    def test_portfolio_dna_crypto_heavy(self):
        assets = [self._make_asset('BTC', 'crypto', 1, 50000, 55000)]
        result = calculate_portfolio_dna(assets)
        self.assertIsNotNone(result)
        self.assertEqual(result['personality'], 'Crypto Maximalist')

# ─── Cache Tests ────────────────────────────────────────────────

class CacheTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.client.login(username='testuser', password='testpass123')

    def test_dashboard_loads_with_cache(self):
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)
        # İkinci yükleme cache'den gelmeli
        response2 = self.client.get(reverse('dashboard'))
        self.assertEqual(response2.status_code, 200)

    def test_market_page_loads(self):
        response = self.client.get(reverse('market'))
        self.assertEqual(response.status_code, 200)


# ─── New Analytics View Tests ────────────────────────────────────

class AnalyticsViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.portfolio = Portfolio.objects.create(user=self.user, name='Test')
        self.asset = Asset.objects.create(
            portfolio=self.portfolio, symbol='AAPL', name='Apple',
            asset_type='stock', quantity=Decimal('5'), avg_buy_price=Decimal('150')
        )
        PriceHistory.objects.create(asset=self.asset, price=Decimal('160'))
        self.client.login(username='testuser', password='testpass123')

    def test_market_mood_loads(self):
        response = self.client.get(reverse('market_mood'))
        self.assertEqual(response.status_code, 200)

    def test_market_mood_requires_auth(self):
        self.client.logout()
        response = self.client.get(reverse('market_mood'))
        self.assertEqual(response.status_code, 302)

    def test_market_mood_has_context(self):
        response = self.client.get(reverse('market_mood'))
        self.assertIn('mood', response.context)

    def test_earnings_calendar_loads(self):
        response = self.client.get(reverse('earnings_calendar'))
        self.assertEqual(response.status_code, 200)

    def test_earnings_calendar_requires_auth(self):
        self.client.logout()
        response = self.client.get(reverse('earnings_calendar'))
        self.assertEqual(response.status_code, 302)

    def test_short_squeeze_loads(self):
        response = self.client.get(reverse('short_squeeze'))
        self.assertEqual(response.status_code, 200)

    def test_short_squeeze_requires_auth(self):
        self.client.logout()
        response = self.client.get(reverse('short_squeeze'))
        self.assertEqual(response.status_code, 302)

    def test_famous_investors_loads(self):
        response = self.client.get(reverse('famous_investors'))
        self.assertEqual(response.status_code, 200)

    def test_famous_investors_has_context(self):
        response = self.client.get(reverse('famous_investors'))
        self.assertIn('famous', response.context)
        self.assertIn('user_return', response.context)

    def test_crisis_sim_loads(self):
        response = self.client.get(reverse('crisis_sim'))
        self.assertEqual(response.status_code, 200)

    def test_crisis_sim_requires_auth(self):
        self.client.logout()
        response = self.client.get(reverse('crisis_sim'))
        self.assertEqual(response.status_code, 302)

    def test_crisis_sim_2008(self):
        response = self.client.get(reverse('crisis_sim') + '?crisis=2008_financial')
        self.assertEqual(response.status_code, 200)
        self.assertIn('result', response.context)

    def test_crisis_sim_covid(self):
        response = self.client.get(reverse('crisis_sim') + '?crisis=2020_covid')
        self.assertEqual(response.status_code, 200)

    def test_crisis_sim_crypto_winter(self):
        response = self.client.get(reverse('crisis_sim') + '?crisis=2022_crypto_winter')
        self.assertEqual(response.status_code, 200)

    def test_economic_calendar_loads(self):
        response = self.client.get(reverse('economic_calendar'))
        self.assertEqual(response.status_code, 200)

    def test_economic_calendar_filter_high(self):
        response = self.client.get(reverse('economic_calendar') + '?impact=high')
        self.assertEqual(response.status_code, 200)

    def test_economic_calendar_filter_medium(self):
        response = self.client.get(reverse('economic_calendar') + '?impact=medium')
        self.assertEqual(response.status_code, 200)

    def test_bist_market_loads(self):
        response = self.client.get(reverse('bist_market'))
        self.assertEqual(response.status_code, 200)

    def test_bist_market_has_context(self):
        response = self.client.get(reverse('bist_market'))
        self.assertIn('usd_try', response.context)

    def test_volatility_chart_loads(self):
        response = self.client.get(reverse('volatility_chart'))
        self.assertEqual(response.status_code, 200)

    def test_monte_carlo_loads(self):
        response = self.client.get(reverse('monte_carlo'))
        self.assertEqual(response.status_code, 200)

    def test_monte_carlo_with_params(self):
        response = self.client.get(reverse('monte_carlo') + '?days=126&sims=200')
        self.assertEqual(response.status_code, 200)

    def test_efficient_frontier_loads(self):
        response = self.client.get(reverse('efficient_frontier'))
        self.assertEqual(response.status_code, 200)

    def test_sector_rotation_loads(self):
        response = self.client.get(reverse('sector_rotation'))
        self.assertEqual(response.status_code, 200)

    def test_ipo_tracker_loads(self):
        response = self.client.get(reverse('ipo_tracker'))
        self.assertEqual(response.status_code, 200)

    def test_insider_trading_loads(self):
        response = self.client.get(reverse('insider_trading'))
        self.assertEqual(response.status_code, 200)

    def test_portfolio_beta_loads(self):
        response = self.client.get(reverse('portfolio_beta'))
        self.assertEqual(response.status_code, 200)

    def test_price_targets_loads(self):
        response = self.client.get(reverse('price_targets'))
        self.assertEqual(response.status_code, 200)

    def test_dca_planner_loads(self):
        response = self.client.get(reverse('dca_planner'))
        self.assertEqual(response.status_code, 200)

    def test_dca_planner_post(self):
        response = self.client.post(reverse('dca_planner'), {
            'symbol': 'AAPL',
            'asset_type': 'stock',
            'monthly_amount': '100',
            'months': '12',
            'expected_return': '10',
        })
        self.assertEqual(response.status_code, 200)

    def test_portfolio_comparison_loads(self):
        response = self.client.get(reverse('portfolio_comparison'))
        self.assertEqual(response.status_code, 200)


# ─── Crisis Simulator Service Tests ─────────────────────────────

class CrisisSimulatorTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass123')
        self.portfolio = Portfolio.objects.create(user=self.user, name='Test')
        self.asset_stock = Asset.objects.create(
            portfolio=self.portfolio, symbol='AAPL', name='Apple',
            asset_type='stock', quantity=Decimal('10'), avg_buy_price=Decimal('150')
        )
        self.asset_crypto = Asset.objects.create(
            portfolio=self.portfolio, symbol='BTC', name='Bitcoin',
            asset_type='crypto', quantity=Decimal('1'), avg_buy_price=Decimal('50000')
        )
        PriceHistory.objects.create(asset=self.asset_stock, price=Decimal('160'))
        PriceHistory.objects.create(asset=self.asset_crypto, price=Decimal('55000'))

    def test_crisis_simulator_2008(self):
        from .services import crisis_simulator
        assets = list(Asset.objects.filter(portfolio=self.portfolio).prefetch_related('prices'))
        result = crisis_simulator(assets, '2008_financial')
        self.assertIsNotNone(result)
        self.assertIn('total_loss', result)
        self.assertIn('scenario_value', result)
        self.assertIn('asset_results', result)
        self.assertLess(result['total_drop_pct'], 0)

    def test_crisis_simulator_covid(self):
        from .services import crisis_simulator
        assets = list(Asset.objects.filter(portfolio=self.portfolio).prefetch_related('prices'))
        result = crisis_simulator(assets, '2020_covid')
        self.assertIsNotNone(result)
        self.assertLess(result['scenario_value'], result['total_value'])

    def test_crisis_simulator_crypto_winter(self):
        from .services import crisis_simulator
        assets = list(Asset.objects.filter(portfolio=self.portfolio).prefetch_related('prices'))
        result = crisis_simulator(assets, '2022_crypto_winter')
        self.assertIsNotNone(result)

    def test_crisis_simulator_invalid(self):
        from .services import crisis_simulator
        assets = list(Asset.objects.filter(portfolio=self.portfolio).prefetch_related('prices'))
        result = crisis_simulator(assets, 'invalid_crisis')
        self.assertIsNone(result)

    def test_crisis_simulator_empty_assets(self):
        from .services import crisis_simulator
        result = crisis_simulator([], '2008_financial')
        self.assertIsNone(result)

    def test_crisis_scenario_value_less_than_current(self):
        from .services import crisis_simulator
        assets = list(Asset.objects.filter(portfolio=self.portfolio).prefetch_related('prices'))
        result = crisis_simulator(assets, '2008_financial')
        self.assertLess(result['scenario_value'], result['total_value'])

    def test_crisis_has_asset_results(self):
        from .services import crisis_simulator
        assets = list(Asset.objects.filter(portfolio=self.portfolio).prefetch_related('prices'))
        result = crisis_simulator(assets, '2008_financial')
        self.assertEqual(len(result['asset_results']), 2)


# ─── Market Mood Service Tests ───────────────────────────────────

class MarketMoodServiceTest(TestCase):
    def test_market_mood_returns_dict(self):
        from .services import get_market_mood
        from django.core.cache import cache
        cache.clear()
        result = get_market_mood()
        self.assertIsNotNone(result)
        self.assertIn('score', result)
        self.assertIn('mood', result)
        self.assertIn('emoji', result)
        self.assertIn('color', result)

    def test_market_mood_score_range(self):
        from .services import get_market_mood
        result = get_market_mood()
        self.assertGreaterEqual(result['score'], 0)
        self.assertLessEqual(result['score'], 100)

    def test_market_mood_has_indicators(self):
        from .services import get_market_mood
        result = get_market_mood()
        self.assertIn('indicators', result)


# ─── Economic Calendar Service Tests ────────────────────────────

class EconomicCalendarTest(TestCase):
    def test_economic_calendar_returns_list(self):
        from .services import get_economic_calendar
        result = get_economic_calendar()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_economic_calendar_has_required_fields(self):
        from .services import get_economic_calendar
        result = get_economic_calendar()
        if result:
            event = result[0]
            self.assertIn('date', event)
            self.assertIn('event', event)
            self.assertIn('country', event)
            self.assertIn('impact', event)
            self.assertIn('flag', event)

    def test_economic_calendar_sorted_by_date(self):
        from .services import get_economic_calendar
        result = get_economic_calendar()
        dates = [e['date'] for e in result]
        self.assertEqual(dates, sorted(dates))


# ─── Famous Investors Service Tests ─────────────────────────────

class FamousInvestorsTest(TestCase):
    def test_famous_portfolios_returns_list(self):
        from .services import get_famous_portfolios
        result = get_famous_portfolios()
        self.assertIsInstance(result, list)
        self.assertGreater(len(result), 0)

    def test_famous_portfolios_has_required_fields(self):
        from .services import get_famous_portfolios
        result = get_famous_portfolios()
        for investor in result:
            self.assertIn('name', investor)
            self.assertIn('emoji', investor)
            self.assertIn('holdings', investor)
            self.assertIn('daily_return', investor)