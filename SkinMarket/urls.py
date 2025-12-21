from django.contrib import admin
from django.urls import path
from . import views

app_name = 'SkinMarket'

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home_view, name='home'),
    path('login/', views.steam_login, name='login'),
    path('callback/', views.steam_callback, name='callback'),
    path('logout/', views.logout_view, name='logout'),
    path('api/inventory/', views.get_steam_inventory, name='api_inventory'),
    path('profile/', views.profile_view, name='profile'),
    path('compare/', views.compare_prices_view, name='comparison_price'),
    path('api/market-data/', views.get_market_data_api, name='market_data_api'),
    path('pricing/', views.pricing_view, name='pricing'),
    path('skin/<str:skin_name>/', views.skin_detail_view, name='skin_detail'),
    path('skin/<str:skin_name>/<str:wear>/', views.skin_detail_view, name='skin_detail_with_wear'),
    path('api/skin/<str:skin_name>/data/', views.get_skin_data_api, name='skin_data_api'),
    path('api/skin/<str:skin_name>/prices/', views.get_skin_prices_api, name='skin_prices_api'),
    path('api/skin/<str:skin_name>/history/', views.get_skin_history_api, name='skin_history_api'),
]