# urls.py
from django.urls import path
from . import views

app_name = 'steam_auth'

urlpatterns = [
    path('login/', views.steam_login, name='login'),
    path('callback/', views.steam_callback, name='callback'),
    path('logout/', views.logout_view, name='logout'),
    path('api/inventory/', views.get_steam_inventory, name='api_inventory'),
    path('profile/', views.profile_view, name='profile'),
    path('compare/', views.compare_prices_view, name='comparison_price'),
    path('api/market-data/', views.get_market_data_api, name='market_data_api'),

    # Добавляем этот путь для JS
    path('api/get_items/', views.get_market_data_api, name='get_items_api'),
]
