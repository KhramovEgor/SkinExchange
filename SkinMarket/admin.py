from django.contrib import admin
from .models import SteamUser

@admin.register(SteamUser)
class SteamUserAdmin(admin.ModelAdmin):
    list_display = ('persona_name', 'steam_id', 'user', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('persona_name', 'steam_id', 'user__username')
    readonly_fields = ('created_at', 'updated_at')
    fieldsets = (
        (None, {
            'fields': ('user', 'steam_id', 'persona_name')
        }),
        ('Профиль Steam', {
            'fields': ('profile_url', 'avatar', 'avatar_medium', 'avatar_full'),
            'classes': ('collapse',)
        }),
        ('Даты', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )