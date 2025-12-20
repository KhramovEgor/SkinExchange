from django.contrib.auth.models import AbstractUser
from django.db import models
from decimal import Decimal

class User(AbstractUser):
    steam_id = models.CharField(max_length=100, blank=True, null=True)
    avatar_url = models.URLField(max_length=500, blank=True, null=True)
    
    # KYC поля
    kyc_verified = models.BooleanField(default=False)
    kyc_status = models.CharField(
        max_length=20,
        choices=[
            ('NOT_SUBMITTED', 'Не отправлен'),
            ('PENDING', 'На проверке'),
            ('VERIFIED', 'Верифицирован'),
            ('REJECTED', 'Отклонен'),
            ('REQUIRES_REVIEW', 'Требует повторной проверки'),
        ],
        default='NOT_SUBMITTED'
    )
    kyc_submitted_at = models.DateTimeField(null=True, blank=True)
    kyc_verified_at = models.DateTimeField(null=True, blank=True)
    
    # ДОБАВЛЯЕМ related_name чтобы избежать конфликтов:
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='core_user_set',  # ← ДОБАВЬТЕ ЭТО
        related_query_name='user'
    )
    
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='core_user_set',  # ← ДОБАВЬТЕ ЭТО
        related_query_name='user'
    )
    
    class Meta:
        db_table = 'core_user'
    
    def __str__(self):
        return self.username
    
    @property
    def balance(self):
        """Текущий баланс пользователя"""
        try:
            return self.user_balance.amount
        except UserBalance.DoesNotExist:
            # Создаем баланс при первом обращении
            balance = UserBalance.objects.create(user=self, amount=Decimal('0'))
            return balance.amount
    
    def get_available_balance(self):
        """Доступный для торговли баланс"""
        try:
            return self.user_balance.amount
        except UserBalance.DoesNotExist:
            return Decimal('0')

class UserBalance(models.Model):
    """Баланс пользователя"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='user_balance')
    amount = models.DecimalField(max_digits=12, decimal_places=2, default=0)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'core_userbalance'
        verbose_name = 'Баланс пользователя'
        verbose_name_plural = 'Балансы пользователей'
    
    def __str__(self):
        return f"{self.user.username}: {self.amount}"
    
    def deposit(self, amount):
        """Пополнение баланса"""
        from decimal import Decimal
        self.amount += Decimal(str(amount))
        self.save()
        return self
    
    def withdraw(self, amount):
        """Списание с баланса"""
        from decimal import Decimal
        amount_decimal = Decimal(str(amount))
        if self.amount >= amount_decimal:
            self.amount -= amount_decimal
            self.save()
            return True
        return False
    
    def has_sufficient_funds(self, amount):
        """Проверка достаточности средств"""
        from decimal import Decimal
        return self.amount >= Decimal(str(amount))