from django.db import models
from django.conf import settings

class UserSkin(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    skin = models.ForeignKey('catalog.Skin', on_delete=models.CASCADE)
    asset_id = models.CharField(max_length=100, unique=True)
    
    def __str__(self):
        return f"{self.user.username}: {self.skin.name}"