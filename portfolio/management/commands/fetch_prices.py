from django.core.management.base import BaseCommand
from portfolio.models import Asset, PriceHistory
from portfolio.services import fetch_price


class Command(BaseCommand):
    help = 'Fetch latest prices for all assets'

    def handle(self, *args, **kwargs):
        assets = Asset.objects.all()
        updated = 0
        for asset in assets:
            try:
                price = fetch_price(asset)
                if price:
                    PriceHistory.objects.create(asset=asset, price=price)
                    updated += 1
                    self.stdout.write(f'✓ {asset.symbol}: ${price}')
            except Exception as e:
                self.stdout.write(f'✗ {asset.symbol}: {e}')
        self.stdout.write(f'Updated {updated}/{assets.count()} assets')