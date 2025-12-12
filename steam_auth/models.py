from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class SteamUser(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='steam_profile'
    )
    steam_id = models.CharField(
        max_length=17,
        unique=True,
        verbose_name='Steam ID'
    )
    persona_name = models.CharField(
        max_length=255,
        blank=True,
        verbose_name='Имя в Steam'
    )
    profile_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='URL профиля'
    )
    avatar = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='Маленький аватар'
    )
    avatar_medium = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='Средний аватар'
    )
    avatar_full = models.URLField(
        max_length=500,
        blank=True,
        verbose_name='Полный аватар'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Steam пользователь'
        verbose_name_plural = 'Steam пользователи'

    def __str__(self):
        return f'{self.persona_name} ({self.steam_id})'


@receiver(post_save, sender=User)
def create_steam_profile(sender, instance, created, **kwargs):
    if created:
        SteamUser.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_steam_profile(sender, instance, **kwargs):
    if hasattr(instance, 'steam_profile'):
        instance.steam_profile.save()