from django.contrib import admin
from .models import Order, Transaction

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'skin', 'order_type', 'price', 'quantity', 'status', 'created_at')
    list_filter = ('order_type', 'status', 'created_at')
    search_fields = ('user__username', 'skin__name')
    ordering = ('-created_at',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('id', 'buyer', 'seller', 'skin', 'price', 'quantity', 'executed_at')
    list_filter = ('executed_at',)
    search_fields = ('buyer__username', 'seller__username', 'skin__name')
    ordering = ('-executed_at',)