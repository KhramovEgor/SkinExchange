"""
URL configuration for SkinExchange project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from django.contrib import admin
from django.urls import path, include

from steam_auth import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('steam_auth.urls')),
    path('', views.home_view, name='home'),
    path('profile/', views.profile_view, name='profile'),
    path('api/inventory/', views.get_steam_inventory, name='api_inventory'),
    path('pricing/', views.pricing_view, name='pricing'),
    path('skin/<str:skin_name>/', views.skin_detail_view, name='skin_detail'),
    path('skin/<str:skin_name>/<str:wear>/', views.skin_detail_view, name='skin_detail_with_wear'),
    path('api/skin/<str:skin_name>/data/', views.get_skin_data_api, name='skin_data_api'),
    path('api/skin/<str:skin_name>/prices/', views.get_skin_prices_api, name='skin_prices_api'),
    path('api/skin/<str:skin_name>/history/', views.get_skin_history_api, name='skin_history_api'),
]
