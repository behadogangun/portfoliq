from rest_framework import serializers, viewsets, permissions
from portfolio.models import Portfolio, Asset, Transaction


class AssetSerializer(serializers.ModelSerializer):
    current_value = serializers.SerializerMethodField()
    profit_loss_percent = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = ['id', 'symbol', 'name', 'asset_type', 'quantity',
                  'avg_buy_price', 'current_value', 'profit_loss_percent']

    def get_current_value(self, obj):
        return round(obj.current_value(), 2)

    def get_profit_loss_percent(self, obj):
        return round(obj.profit_loss_percent(), 2)


class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'transaction_type', 'quantity', 'price', 'date', 'note']


class PortfolioSerializer(serializers.ModelSerializer):
    assets = AssetSerializer(many=True, read_only=True)
    total_value = serializers.SerializerMethodField()

    class Meta:
        model = Portfolio
        fields = ['id', 'name', 'description', 'created_at', 'total_value', 'assets']

    def get_total_value(self, obj):
        return round(obj.total_value(), 2)


class PortfolioViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = PortfolioSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Portfolio.objects.filter(user=self.request.user)


class AssetViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = AssetSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Asset.objects.filter(portfolio__user=self.request.user)