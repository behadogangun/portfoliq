from django import forms
from .models import Portfolio, Asset, Transaction


class PortfolioForm(forms.ModelForm):
    class Meta:
        model = Portfolio
        fields = ['name', 'description']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'pq-input', 'placeholder': 'Portföy adı'}),
            'description': forms.Textarea(attrs={'class': 'pq-input', 'rows': 3, 'placeholder': 'Açıklama (isteğe bağlı)'}),
        }


class AssetForm(forms.ModelForm):
    class Meta:
        model = Asset
        fields = ['symbol', 'name', 'asset_type', 'quantity', 'avg_buy_price']
        widgets = {
            'symbol': forms.TextInput(attrs={'class': 'pq-input', 'placeholder': 'BTC, AAPL, XAU...'}),
            'name': forms.TextInput(attrs={'class': 'pq-input', 'placeholder': 'Bitcoin, Apple Inc...'}),
            'asset_type': forms.Select(attrs={'class': 'pq-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'pq-input', 'step': '0.00000001'}),
            'avg_buy_price': forms.NumberInput(attrs={'class': 'pq-input', 'step': '0.01'}),
        }


class TransactionForm(forms.ModelForm):
    class Meta:
        model = Transaction
        fields = ['transaction_type', 'quantity', 'price', 'date', 'note']
        widgets = {
            'transaction_type': forms.Select(attrs={'class': 'pq-input'}),
            'quantity': forms.NumberInput(attrs={'class': 'pq-input', 'step': '0.00000001'}),
            'price': forms.NumberInput(attrs={'class': 'pq-input', 'step': '0.01'}),
            'date': forms.DateTimeInput(attrs={'class': 'pq-input', 'type': 'datetime-local'}),
            'note': forms.Textarea(attrs={'class': 'pq-input', 'rows': 2}),
        }