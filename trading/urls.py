from django.urls import path
from .views import OrderCreateView, OrderListView, TransactionListView

urlpatterns = [
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/create/', OrderCreateView.as_view(), name='order-create'),
    path('transactions/', TransactionListView.as_view(), name='transaction-list'),
]