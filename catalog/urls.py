from django.urls import path
from . import views

urlpatterns = [
    path('', views.skin_list, name='skin_list'),
]