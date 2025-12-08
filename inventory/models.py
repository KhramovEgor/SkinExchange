from django.db import models
from core.models import User
from catalog.models import Skin

class UserSkin(models.Model):
    STATUS_CHOICES = [
        ('available', 'Доступен'),
        ('in_trade', 'В обмене'),
        ('sold', 'Продан'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='skins')
    skin = models.ForeignKey(Skin, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    acquired_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'inventory_userskin'
        verbose_name = 'Скин пользователя'
        verbose_name_plural = 'Скины пользователей'
        unique_together = ['user', 'skin']
    
    def __str__(self):
        return f"{self.user.username} - {self.skin.name}"