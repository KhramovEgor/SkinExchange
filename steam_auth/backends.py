from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .models import SteamUser

class SteamBackend(BaseBackend):
    def authenticate(self, request, steam_id=None, **kwargs):
        try:
            steam_user = SteamUser.objects.get(steam_id=steam_id)
            return steam_user.user
        except SteamUser.DoesNotExist:
            user = User.objects.create(
                username=f'steam_{steam_id}',
                password='not_used'
            )
            steam_user, created = SteamUser.objects.update_or_create(
                user=user,
                defaults={'steam_id': steam_id}
            )
            return user
        except Exception as e:
            print(f"Ошибка аутентификации: {e}")
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None