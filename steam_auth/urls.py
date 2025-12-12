from django.urls import path
from . import views

app_name = 'steam_auth'

urlpatterns = [
    path('', views.home_view, name='home'),
    path('login/', views.steam_login, name='login'),
    path('callback/', views.steam_callback, name='callback'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name='profile'),
]