from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'portfolios', views.PortfolioViewSet, basename='api-portfolio')
router.register(r'assets', views.AssetViewSet, basename='api-asset')

urlpatterns = [
    path('', include(router.urls)),
]