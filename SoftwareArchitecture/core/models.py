from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    steam_id = models.CharField(max_length=20, blank=True, null=True, unique=True)
    steam_profile = models.URLField(blank=True, null=True)
    kyc_status = models.CharField(max_length=20, default='not_verified')
    balance = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.username} ({self.steam_id or 'no Steam'})"