from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from .models import SteamUser


class SteamBackend(BaseBackend):
    def authenticate(self, request, steam_id=None, **kwargs):
        try:
            # 1. Пытаемся найти пользователя через SteamUser
            steam_user = SteamUser.objects.get(steam_id=steam_id)
            print(f"[DEBUG] Найден существующий пользователь: {steam_user.user.username}")
            return steam_user.user

        except SteamUser.DoesNotExist:
            try:
                # 2. Если пользователь с таким steam_id не найден, создаем нового
                # Используем username на основе Steam ID
                username = f'steam_{steam_id}'

                # Проверяем, не существует ли уже пользователь с таким username
                # (на случай если пользователь был создан другим способом)
                user, created = User.objects.get_or_create(
                    username=username,
                    defaults={'password': 'not_used'}
                )

                if created:
                    print(f"[DEBUG] Создан новый пользователь: {username}")
                else:
                    print(f"[DEBUG] Найден существующий пользователь по username: {username}")

                # Создаем связь с SteamUser
                steam_user, steam_created = SteamUser.objects.get_or_create(
                    user=user,
                    defaults={'steam_id': steam_id}
                )

                if steam_created:
                    print(f"[DEBUG] Создана связь SteamUser для {username}")
                else:
                    print(f"[DEBUG] Связь SteamUser уже существует для {username}")

                return user

            except Exception as e:
                print(f"[ERROR] Ошибка при создании пользователя: {e}")
                return None

        except Exception as e:
            print(f"[ERROR] Ошибка аутентификации: {e}")
            return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None