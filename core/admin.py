from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, UserBalance

# Расширяем стандартный UserAdmin для нашей модели User
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'steam_id', 'kyc_status', 'balance', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Steam данные', {'fields': ('steam_id', 'avatar_url')}),
        ('KYC данные', {'fields': ('kyc_verified', 'kyc_status', 'kyc_submitted_at', 'kyc_verified_at')}),
    )
    list_filter = UserAdmin.list_filter + ('kyc_status',)

@admin.register(UserBalance)
class UserBalanceAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'updated_at')
    search_fields = ('user__username',)
    ordering = ('-updated_at',)

# Регистрируем нашу модель User
admin.site.register(User, CustomUserAdmin)