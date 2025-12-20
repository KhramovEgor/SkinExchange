from django.db import models
from django.contrib.auth import get_user_model
from catalog.models import Skin  # Предполагаем, что у вас есть модель Skin в catalog

User = get_user_model()  # Теперь это будет core.User

class Order(models.Model):
    ORDER_TYPES = [
        ('BUY', 'Buy'),
        ('SELL', 'Sell'),
    ]
    ORDER_STATUSES = [
        ('PENDING', 'Pending'),
        ('EXECUTED', 'Executed'),
        ('CANCELLED', 'Cancelled'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    skin = models.ForeignKey(Skin, on_delete=models.CASCADE, related_name='orders')
    order_type = models.CharField(max_length=4, choices=ORDER_TYPES)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    status = models.CharField(max_length=10, choices=ORDER_STATUSES, default='PENDING')
    created_at = models.DateTimeField(auto_now_add=True)
    executed_at = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.order_type} {self.quantity} x {self.skin.name} @ {self.price}"

class Transaction(models.Model):
    buyer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='buy_transactions')
    seller = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sell_transactions')
    skin = models.ForeignKey(Skin, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField()
    executed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.skin.name} {self.quantity} @ {self.price}"