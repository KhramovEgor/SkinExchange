from django.urls import path
from . import views

urlpatterns = [
    path('', views.user_inventory, name='user_inventory'),
]