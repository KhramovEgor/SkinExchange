from django.urls import path
from . import views

urlpatterns = [
    path('login/', views.steam_login, name='steam_login'),
    path('callback/', views.steam_callback, name='steam_callback'),
]