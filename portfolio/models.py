from django.db import models
from django.contrib.auth.models import User


class Portfolio(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='portfolios')
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.username} - {self.name}"

    def total_value(self):
        return sum(asset.current_value() for asset in self.assets.all())


class Asset(models.Model):
    ASSET_TYPES = [
    ('stock', 'Stock'),
    ('crypto', 'Crypto'),
    ('gold', 'Gold'),
    ('currency', 'Currency'),
    ('other', 'Other'),
]

    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE, related_name='assets')
    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=20, choices=ASSET_TYPES)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    avg_buy_price = models.DecimalField(max_digits=20, decimal_places=2)
    logo = models.URLField(blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol} ({self.get_asset_type_display()})"

    def total_cost(self):
        return float(self.quantity) * float(self.avg_buy_price)

    def current_value(self):
        latest = self.prices.order_by('-timestamp').first()
        if latest:
            return float(self.quantity) * float(latest.price)
        return self.total_cost()

    def profit_loss(self):
        return self.current_value() - self.total_cost()

    def profit_loss_percent(self):
        if self.total_cost() == 0:
            return 0
        return (self.profit_loss() / self.total_cost()) * 100


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('buy', 'Alış'),
        ('sell', 'Satış'),
    ]

    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='transactions')
    transaction_type = models.CharField(max_length=4, choices=TRANSACTION_TYPES)
    quantity = models.DecimalField(max_digits=20, decimal_places=8)
    price = models.DecimalField(max_digits=20, decimal_places=2)
    date = models.DateTimeField()
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.get_transaction_type_display()} - {self.asset.symbol} x{self.quantity}"

    def total_amount(self):
        return float(self.quantity) * float(self.price)


class PriceHistory(models.Model):
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='prices')
    price = models.DecimalField(max_digits=20, decimal_places=2)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-timestamp']

    def __str__(self):
        return f"{self.asset.symbol} - {self.price} @ {self.timestamp}"
    

class PriceAlert(models.Model):
    ALERT_TYPES = [
        ('above', 'Price goes above'),
        ('below', 'Price goes below'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='alerts')
    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=20)
    logo = models.URLField(blank=True, default='')
    target_price = models.DecimalField(max_digits=20, decimal_places=2)
    alert_type = models.CharField(max_length=10, choices=ALERT_TYPES)
    is_triggered = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.symbol} {self.alert_type} ${self.target_price}"


class WatchlistItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='watchlist')
    symbol = models.CharField(max_length=20)
    name = models.CharField(max_length=100)
    asset_type = models.CharField(max_length=20)
    logo = models.URLField(blank=True, default='')
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'symbol']

    def __str__(self):
        return f"{self.user.username} — {self.symbol}"
    
def current_price(self):
    latest = self.prices.order_by('-timestamp').first()
    return float(latest.price) if latest else float(self.avg_buy_price)