from django.contrib import admin
from .models import Skin

@admin.register(Skin)
class SkinAdmin(admin.ModelAdmin):
    list_display = ('name', 'type', 'rarity', 'price', 'price_updated')
    list_filter = ('type', 'rarity')
    search_fields = ('name', 'skin_id')