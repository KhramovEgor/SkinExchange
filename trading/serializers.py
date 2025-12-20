from rest_framework import serializers
from .models import Order, Transaction

class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['id', 'user', 'skin', 'order_type', 'price', 'quantity', 'status', 'created_at']
        read_only_fields = ['user', 'status', 'created_at']

class TransactionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Transaction
        fields = ['id', 'buyer', 'seller', 'skin', 'price', 'quantity', 'executed_at']