from django.contrib import admin
from .models import Portfolio, Asset, Transaction, PriceHistory


@admin.register(Portfolio)
class PortfolioAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'created_at']
    list_filter = ['user']
    search_fields = ['name', 'user__username']


@admin.register(Asset)
class AssetAdmin(admin.ModelAdmin):
    list_display = ['symbol', 'name', 'asset_type', 'quantity', 'avg_buy_price', 'portfolio']
    list_filter = ['asset_type']
    search_fields = ['symbol', 'name']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['asset', 'transaction_type', 'quantity', 'price', 'date']
    list_filter = ['transaction_type']


@admin.register(PriceHistory)
class PriceHistoryAdmin(admin.ModelAdmin):
    list_display = ['asset', 'price', 'timestamp']
    list_filter = ['asset']