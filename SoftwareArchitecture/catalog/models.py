from django.db import models

class Skin(models.Model):
    name = models.CharField(max_length=200)
    skin_id = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=100)
    rarity = models.CharField(max_length=50)
    image_url = models.URLField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_updated = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.name} - {self.price} руб."