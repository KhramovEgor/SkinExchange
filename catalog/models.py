from django.db import models

class Skin(models.Model):
    RARITY_CHOICES = [
        ('common', 'Обычный'),
        ('uncommon', 'Необычный'),
        ('rare', 'Редкий'),
        ('mythical', 'Мифический'),
        ('legendary', 'Легендарный'),
        ('ancient', 'Древний'),
        ('immortal', 'Бессмертный'),
    ]
    
    name = models.CharField(max_length=255, verbose_name='Название')
    skin_type = models.CharField(max_length=100, verbose_name='Тип')
    rarity = models.CharField(max_length=20, choices=RARITY_CHOICES, verbose_name='Редкость')
    image_url = models.URLField(max_length=500, verbose_name='Изображение')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Цена')
    metadata = models.JSONField(default=dict, blank=True, verbose_name='Метаданные')
    
    external_id = models.CharField(max_length=100, blank=True, null=True, unique=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'catalog_skin'
        verbose_name = 'Скин'
        verbose_name_plural = 'Скины'
    
    def __str__(self):
        return f"{self.name} ({self.get_rarity_display()})"