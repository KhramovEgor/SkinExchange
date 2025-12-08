from django.contrib import admin
from .models import UserSkin

@admin.register(UserSkin)
class UserSkinAdmin(admin.ModelAdmin):
    list_display = ('user', 'skin', 'asset_id')
    list_filter = ('user',)
    search_fields = ('user__username', 'skin__name', 'asset_id')