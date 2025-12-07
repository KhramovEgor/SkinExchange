from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'steam_id', 'kyc_status', 'balance')
    fieldsets = UserAdmin.fieldsets + (
        ('Steam информация', {'fields': ('steam_id', 'steam_profile')}),
        ('KYC информация', {'fields': ('kyc_status',)}),
        ('Финансы', {'fields': ('balance',)}),
    )