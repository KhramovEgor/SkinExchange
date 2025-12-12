import re
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.urls import reverse


def home_view(request):
    context = {
        'user': request.user,
    }
    return render(request, 'steam_auth/home.html', context)


def steam_login(request):
    if request.user.is_authenticated:
        messages.info(request, "Вы уже авторизованы!")
        return redirect('home')

    next_url = request.GET.get('next') or request.POST.get('next') or 'home'

    request.session['login_next_url'] = next_url

    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': request.build_absolute_uri(
            reverse('steam_auth:callback')
        ),
        'openid.realm': request.build_absolute_uri('/'),
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
    }

    if request.method == 'POST':
        print("POST запрос на вход через Steam")

    print(f"[DEBUG] Отправка запроса к Steam OpenID")
    print(f"[DEBUG] Return URL: {params['openid.return_to']}")
    print(f"[DEBUG] Realm: {params['openid.realm']}")

    steam_openid_url = 'https://steamcommunity.com/openid/login'
    query_string = urlencode(params)
    auth_url = f'{steam_openid_url}?{query_string}'

    if settings.DEBUG:
        print(f"[DEBUG] Steam Auth URL: {auth_url}")

    return redirect(auth_url)


def steam_callback(request):
    print(f"[DEBUG] Callback получил параметры: {dict(request.GET)}")

    required_params = [
        'openid.ns',
        'openid.mode',
        'openid.op_endpoint',
        'openid.claimed_id',
        'openid.identity',
        'openid.return_to',
        'openid.response_nonce',
        'openid.assoc_handle',
        'openid.signed',
        'openid.sig'
    ]

    missing_params = [p for p in required_params if p not in request.GET]
    if missing_params:
        messages.error(request, f"Отсутствуют параметры OpenID: {', '.join(missing_params)}")
        return redirect('home')

    if request.GET.get('openid.op_endpoint') != 'https://steamcommunity.com/openid/login':
        messages.error(request, "Ответ получен не от Steam!")
        return redirect('home')

    claimed_id = request.GET.get('openid.claimed_id', '')

    steam_id_match = re.search(r'steamcommunity\.com/openid/id/(\d+)', claimed_id)
    if not steam_id_match:
        messages.error(request, "Неверный формат Steam ID!")
        return redirect('home')

    steam_id = steam_id_match.group(1)
    print(f"[DEBUG] Извлечен Steam ID: {steam_id}")

    if not validate_openid_response(request):
        messages.error(request, "Ошибка валидации OpenID ответа!")
        return redirect('home')

    try:
        api_key = getattr(settings, 'STEAM_API_KEY', '')

        if api_key:
            steam_data = get_steam_user_info(steam_id, api_key)
        else:
            steam_data = {'steam_id': steam_id}
            messages.warning(request, "STEAM_API_KEY не настроен. Некоторые данные недоступны.")

        from .backends import SteamBackend
        backend = SteamBackend()
        user = backend.authenticate(request, steam_id=steam_id)

        if user:
            if steam_data:
                update_user_profile(user, steam_data)

            login(request, user, backend='steam_auth.backends.SteamBackend')

            request.session['steam_data'] = steam_data
            request.session['steam_id'] = steam_id

            messages.success(request, f"Успешный вход! Добро пожаловать!")

            next_url = request.session.pop('login_next_url', 'steam_auth:profile')
            return redirect(next_url)
        else:
            messages.error(request, "Ошибка создания пользователя!")

    except Exception as e:
        print(f"[ERROR] Ошибка в callback: {str(e)}")
        messages.error(request, f"Ошибка авторизации: {str(e)}")

    return redirect('home')


def validate_openid_response(request):
    try:
        if request.GET.get('openid.mode') != 'id_res':
            return False

        nonce = request.GET.get('openid.response_nonce', '')
        if not nonce:
            return False

        return True

    except Exception as e:
        print(f"[ERROR] Ошибка валидации OpenID: {str(e)}")
        return False


def get_steam_user_info(steam_id, api_key):
    try:
        print(f"[DEBUG] Запрос к Steam API для Steam ID: {steam_id}")

        response = requests.get(
            'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/',
            params={
                'key': api_key,
                'steamids': steam_id,
                'format': 'json'
            },
            timeout=10
        )

        print(f"[DEBUG] Steam API статус: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            players = data.get('response', {}).get('players', [])

            if players:
                player = players[0]
                return {
                    'steam_id': steam_id,
                    'persona_name': player.get('personaname', ''),
                    'profile_url': player.get('profileurl', ''),
                    'avatar': player.get('avatar', ''),
                    'avatar_medium': player.get('avatarmedium', ''),
                    'avatar_full': player.get('avatarfull', ''),
                    'real_name': player.get('realname', ''),
                    'country_code': player.get('loccountrycode', ''),
                    'time_created': player.get('timecreated'),
                    'last_logoff': player.get('lastlogoff'),
                    'profile_state': player.get('profilestate'),
                    'community_visibility': player.get('communityvisibilitystate'),
                }
            else:
                print(f"[DEBUG] Игроков не найдено для Steam ID: {steam_id}")
        else:
            print(f"[ERROR] Steam API ошибка: {response.status_code}")

    except requests.RequestException as e:
        print(f"[ERROR] Ошибка запроса к Steam API: {str(e)}")
    except Exception as e:
        print(f"[ERROR] Неожиданная ошибка: {str(e)}")

    return None


def update_user_profile(user, steam_data):
    from .models import SteamUser

    try:
        steam_user, created = SteamUser.objects.get_or_create(
            user=user,
            defaults={'steam_id': steam_data.get('steam_id')}
        )

        update_fields = []

        if 'persona_name' in steam_data:
            steam_user.persona_name = steam_data['persona_name']
            update_fields.append('persona_name')

        if 'profile_url' in steam_data:
            steam_user.profile_url = steam_data['profile_url']
            update_fields.append('profile_url')

        if 'avatar' in steam_data:
            steam_user.avatar = steam_data['avatar']
            update_fields.append('avatar')

        if 'avatar_medium' in steam_data:
            steam_user.avatar_medium = steam_data['avatar_medium']
            update_fields.append('avatar_medium')

        if 'avatar_full' in steam_data:
            steam_user.avatar_full = steam_data['avatar_full']
            update_fields.append('avatar_full')

        if update_fields:
            steam_user.save(update_fields=update_fields)
            print(f"[DEBUG] Обновлен профиль пользователя: {user.username}")

    except Exception as e:
        print(f"[ERROR] Ошибка обновления профиля: {str(e)}")


@login_required
def profile_view(request):
    context = {
        'user': request.user,
        'steam_data': request.session.get('steam_data', {}),
    }
    return render(request, 'steam_auth/profile.html', context)


def logout_view(request):
    logout(request)
    if 'steam_data' in request.session:
        del request.session['steam_data']

    next_url = request.GET.get('next', 'home')
    return redirect(next_url)