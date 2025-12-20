from django.contrib import admin
from .models import Skin

@admin.register(Skin)
class SkinAdmin(admin.ModelAdmin):
    list_display = ('name', 'rarity', 'price', 'last_updated')
    list_filter = ('rarity',)
    search_fields = ('name',)
    ordering = ('-last_updated',)