import re
from urllib.parse import urlencode

import requests
import json
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET


def home_view(request):
    """Главная страница сайта"""
    items_data = [
        {
            "name": "Gamma Case",
            "image": "https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGJKz2lu_XsnXwtmkJjSU91dh8bj35VTqVBP4io_frHEVtvP5bPZrd6XECmOSxe0v4bRoTnnjwBkitWrRm4yoeX3GagMnCZZ2FPlK7EcEv22BnQ/62fx62f",
            "url": "https://steamcommunity.com/market/listings/730/Gamma%20Case",
            "current_price": "477,09 руб."
        },
        {
            "name": "Danger Zone Case",
            "image": "https://community.akamai.steamstatic.com/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGJKz2lu_XsnXwtmkJjSU91dh8bj35VTqVBP4io_fr3MVv_H4a6FucPPBWjDIkbdz4rg4Syyyxxsi5mzRntuvJCqVbwAgDZBwRPlK7EcZJ5GkQA/62fx62f",
            "url": "https://steamcommunity.com/market/listings/730/Danger%20Zone%20Case",
            "current_price": "134,70 руб."
        }
    ]

    steam_data = request.session.get('steam_data', {})

    context = {
        'user': request.user,
        'items_data': items_data,
        'steam_data': steam_data,
        'page_title': 'CS Market Analytics - Главная',
        'market_stats': {
            'daily_volume': '$1.2M',
            'price_change': '+2.34%',
            'active_deals': '12,847',
            'avg_price': '$4.67',
            'total_items': len(items_data)
        }
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

    steam_openid_url = 'https://steamcommunity.com/openid/login'
    query_string = urlencode(params)
    auth_url = f'{steam_openid_url}?{query_string}'

    return redirect(auth_url)


def steam_callback(request):
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

            request.session['steam_data'] = {
                'steam_id': steam_id,
                'persona_name': steam_data.get('persona_name', ''),
                'profile_url': steam_data.get('profile_url', ''),
                'avatar': steam_data.get('avatar', ''),
                'avatar_medium': steam_data.get('avatar_medium', ''),
                'avatar_full': steam_data.get('avatar_full', ''),
                'real_name': steam_data.get('real_name', ''),
                'country_code': steam_data.get('country_code', ''),
                'profile_state': steam_data.get('profile_state', 0),
                'community_visibility': steam_data.get('community_visibility', 0),
            }

            messages.success(request, f"Успешный вход! Добро пожаловать!")

            next_url = request.session.pop('login_next_url', 'steam_auth:profile')
            return redirect(next_url)
        else:
            messages.error(request, "Ошибка создания пользователя!")

    except Exception as e:
        messages.error(request, f"Ошибка авторизации: {str(e)}")

    return redirect('/')


def validate_openid_response(request):
    try:
        if request.GET.get('openid.mode') != 'id_res':
            return False

        nonce = request.GET.get('openid.response_nonce', '')
        if not nonce:
            return False

        return True
    except Exception:
        return False


def get_steam_user_info(steam_id, api_key):
    try:
        response = requests.get(
            'https://api.steampowered.com/ISteamUser/GetPlayerSummaries/v2/',
            params={
                'key': api_key,
                'steamids': steam_id,
                'format': 'json'
            },
            timeout=10
        )

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
                    'profile_state': player.get('profilestate'),
                    'community_visibility': player.get('communityvisibilitystate'),
                }
    except Exception:
        pass

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
    except Exception:
        pass


@login_required
@require_GET
def get_steam_inventory(request):
    """
    API для получения реального инвентаря Steam пользователя
    """
    try:
        # Получаем Steam ID из сессии
        steam_id = "76561198080203313"
        if not steam_id:
            return JsonResponse({
                'error': 'Steam ID не найден в сессии. Пожалуйста, войдите через Steam.',
                'items': []
            }, status=400)

        # Получаем appid из параметров запроса
        appid = request.GET.get('appid', '730')  # По умолчанию CS:GO

        # Карта игр и их contextid
        games = {
            '730': {'name': 'Counter-Strike 2', 'contextid': '2'},
            '570': {'name': 'Dota 2', 'contextid': '2'},
            '440': {'name': 'Team Fortress 2', 'contextid': '2'},
            '252490': {'name': 'Rust', 'contextid': '2'},
            '753': {'name': 'Steam', 'contextid': '6'},  # Карточки Steam
        }

        items = []

        # Загружаем инвентарь для конкретной игры
        game_info = games.get(appid, {'name': f'Game {appid}', 'contextid': '2'})
        items = fetch_steam_inventory(steam_id, appid, game_info['contextid'])

        # Формируем итоговый ответ
        result = {
            'success': True,
            'steam_id': steam_id,
            'appid': appid,
            'total_count': len(items),
            'items': items[:100],  # Ограничиваем для производительности
            'message': f'Загружено {len(items)} предметов из Steam инвентаря'
        }

        return JsonResponse(result)

    except Exception as e:
        return JsonResponse({
            'error': f'Внутренняя ошибка сервера',
            'items': []
        }, status=500)


def fetch_steam_inventory(steam_id, appid, contextid='2'):
    """
    Получение инвентаря из Steam JSON API
    Правильный формат: https://steamcommunity.com/inventory/{steam_id}/{appid}/{contextid}
    """
    try:
        # Формируем URL для нового Steam API
        url = f"https://steamcommunity.com/inventory/{steam_id}/{appid}/{contextid}"

        # Параметры запроса
        params = {
            'l': 'russian',  # Язык
            'count': 100,  # Количество предметов
        }

        # Заголовки
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }

        response = requests.get(url, params=params, headers=headers, timeout=20)

        if response.status_code != 200:
            return []

        # Парсим JSON
        data = response.json()

        # Проверяем успешность запроса
        if not data.get('success'):
            return []

        assets = data.get('assets', [])
        descriptions = data.get('descriptions', [])

        if not assets or not descriptions:
            return []

        # Создаем словарь описаний по classid
        desc_dict = {}
        for desc in descriptions:
            classid = desc.get('classid')
            if classid:
                desc_dict[classid] = desc

        # Обрабатываем предметы
        items = []
        for asset in assets:
            classid = asset.get('classid')

            if classid in desc_dict:
                desc = desc_dict[classid]

                item = {
                    'assetid': asset.get('assetid'),
                    'classid': classid,
                    'instanceid': asset.get('instanceid'),
                    'amount': asset.get('amount', 1),
                    'appid': appid,
                    'contextid': asset.get('contextid'),
                    'name': desc.get('name', ''),
                    'market_hash_name': desc.get('market_hash_name', ''),
                    'market_name': desc.get('market_name', ''),
                    'type': desc.get('type', ''),
                    'tradable': desc.get('tradable', 0) == 1,
                    'marketable': desc.get('marketable', 0) == 1,
                    'commodity': desc.get('commodity', 0) == 1,
                    'icon_url': desc.get('icon_url', ''),
                    'icon_url_large': desc.get('icon_url_large', ''),
                    'tags': desc.get('tags', []),
                }

                # Добавляем информацию о цвете для CS:GO
                if appid == '730' and 'fraudwarnings' in desc:
                    item['fraudwarnings'] = desc['fraudwarnings']

                items.append(item)

        return items

    except Exception:
        return []


@login_required
def profile_view(request):
    """Страница профиля пользователя"""
    steam_data = request.session.get('steam_data', {})

    user_stats = {
        'items_count': 0,
        'games_count': 0,
        'trades_count': 0,
        'inventory_value': 'Загрузка...'
    }

    context = {
        'user': request.user,
        'steam_data': steam_data,
        'user_stats': user_stats,
        'page_title': f'Профиль {steam_data.get("persona_name", request.user.username)}',
    }

    return render(request, 'steam_auth/profile.html', context)


@login_required
def compare_prices_view(request):
    """Страница сравнения цен предметов"""

    # Данные для заглушки (в будущем будут браться из парсера)
    items_data = [
        {
            "name": "Кейс «Киловатт»",
            "hash_name": "Kilowatt Case",
            "price": {
                "lowest_price": "24,76 руб.",
                "median_price": "24,97 руб.",
                "volume": "134,692"
            },
            "image": "https://steamcommunity-a.akamaihd.net/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGJKz2lu_XsnXwtmkJjSU91dh8bj35VTqVBP4io_frnEVvqf_a6VoIfGSXz7Hlbwg57QwSS_mxhl15jiGyN37c3_GZw91W8BwRflK7EfKsa2sfw",
            "url": "https://steamcommunity.com/market/listings/730/Kilowatt%20Case"
        },
        {
            "name": "Капсула с наклейками кандидатов BLAST.tv Paris Major 2023",
            "hash_name": "Paris 2023 Contenders Sticker Capsule",
            "price": {
                "lowest_price": "9,50 руб.",
                "median_price": "9,67 руб.",
                "volume": "40,531"
            },
            "image": "https://steamcommunity-a.akamaihd.net/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGJKz2lu_XsnXwtmkJjSU91dh8bjn_lDkShjjoYbh_ilk__O8Ybc_cKLAMWSfz_pzvuVsXTr9kRki5m_Uwtz7cXKWO1ApCcByRLEO50LtkoWyP7_k4Afdi99GniT4jzQJsHjtsZcvVQ",
            "url": "https://steamcommunity.com/market/listings/730/Paris%202023%20Contenders%20Sticker%20Capsule"
        },
        {
            "name": "Кейс с оружием «Гамма»",
            "hash_name": "Gamma Case",
            "price": {
                "lowest_price": "477,09 руб.",
                "median_price": "480,50 руб.",
                "volume": "89,123"
            },
            "image": "https://steamcommunity-a.akamaihd.net/economy/image/class/730/5661248291/62fx62f",
            "url": "https://steamcommunity.com/market/listings/730/Gamma%20Case"
        },
        {
            "name": "Кейс «Зона опасности»",
            "hash_name": "Danger Zone Case",
            "price": {
                "lowest_price": "134,70 руб.",
                "median_price": "136,20 руб.",
                "volume": "201,456"
            },
            "image": "https://steamcommunity-a.akamaihd.net/economy/image/class/730/5661248289/62fx62f",
            "url": "https://steamcommunity.com/market/listings/730/Danger%20Zone%20Case"
        }
    ]

    # Получаем Steam данные из сессии
    steam_data = request.session.get('steam_data', {})

    # Параметры фильтров из GET запроса
    min_price = request.GET.get('min_price', '0')
    max_price = request.GET.get('max_price', '99999')
    min_profit = request.GET.get('min_profit', '0')
    max_profit = request.GET.get('max_profit', '99999')
    min_liquidity = request.GET.get('min_liquidity', '0')
    max_liquidity = request.GET.get('max_liquidity', '100')
    min_profit_percent = request.GET.get('min_profit_percent', '0')
    max_profit_percent = request.GET.get('max_profit_percent', '100')
    sort_by = request.GET.get('sort_by', 'price')

    # Здесь в будущем будет логика фильтрации данных
    filtered_items = items_data  # Пока отображаем все

    # Статистика для страницы
    market_stats = {
        'total_items': 28699,
        'showing_items': len(filtered_items),
        'avg_price': '17,13 руб.',
        'avg_profit': '2,34%',
        'total_volume': '175,223',
        'price_change': '+2.3%',
        'volume_change': '+15.7%',
        'liquidity_change': '-3.2%'
    }

    context = {
        'user': request.user,
        'steam_data': steam_data,
        'items_data': filtered_items,
        'market_stats': market_stats,
        'filters': {
            'min_price': min_price,
            'max_price': max_price,
            'min_profit': min_profit,
            'max_profit': max_profit,
            'min_liquidity': min_liquidity,
            'max_liquidity': max_liquidity,
            'min_profit_percent': min_profit_percent,
            'max_profit_percent': max_profit_percent,
            'sort_by': sort_by,
        },
        'page_title': 'CS Market Analytics - Сравнение цен',
    }

    return render(request, 'steam_auth/comparison_price.html', context)


@require_GET
def get_market_data_api(request):
    """
    API endpoint для получения рыночных данных (заглушка для парсера)
    В будущем здесь будет реальное подключение к парсеру
    """
    try:
        # Параметры запроса
        limit = int(request.GET.get('limit', 50))
        offset = int(request.GET.get('offset', 0))
        game = request.GET.get('game', '730')  # CS:GO

        # Заглушка данных
        items_data = [
            {
                "name": "Кейс «Киловатт»",
                "hash_name": "Kilowatt Case",
                "price": {
                    "lowest_price": "24,76 руб.",
                    "median_price": "24,97 руб.",
                    "volume": "134,692"
                },
                "image": "https://steamcommunity-a.akamaihd.net/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGJKz2lu_XsnXwtmkJjSU91dh8bj35VTqVBP4io_frnEVvqf_a6VoIfGSXz7Hlbwg57QwSS_mxhl15jiGyN37c3_GZw91W8BwRflK7EfKsa2sfw",
                "url": "https://steamcommunity.com/market/listings/730/Kilowatt%20Case",
                "profit": "0,21 руб.",
                "profit_percent": "0.85%",
                "liquidity": "92%"
            },
            {
                "name": "Капсула с наклейками кандидатов BLAST.tv Paris Major 2023",
                "hash_name": "Paris 2023 Contenders Sticker Capsule",
                "price": {
                    "lowest_price": "9,50 руб.",
                    "median_price": "9,67 руб.",
                    "volume": "40,531"
                },
                "image": "https://steamcommunity-a.akamaihd.net/economy/image/i0CoZ81Ui0m-9KwlBY1L_18myuGuq1wfhWSaZgMttyVfPaERSR0Wqmu7LAocGJKz2lu_XsnXwtmkJjSU91dh8bjn_lDkShjjoYbh_ilk__O8Ybc_cKLAMWSfz_pzvuVsXTr9kRki5m_Uwtz7cXKWO1ApCcByRLEO50LtkoWyP7_k4Afdi99GniT4jzQJsHjtsZcvVQ",
                "url": "https://steamcommunity.com/market/listings/730/Paris%202023%20Contenders%20Sticker%20Capsule",
                "profit": "0,17 руб.",
                "profit_percent": "1.79%",
                "liquidity": "85%"
            }
        ]

        # Фильтрация по параметрам запроса
        min_price = float(request.GET.get('min_price', 0))
        max_price = float(request.GET.get('max_price', 99999))

        filtered_items = []
        for item in items_data:
            # Парсим цену (упрощенно)
            price_str = item['price']['lowest_price'].replace(' руб.', '').replace(',', '.')
            try:
                price = float(price_str)
                if min_price <= price <= max_price:
                    filtered_items.append(item)
            except ValueError:
                pass

        response_data = {
            'success': True,
            'count': len(filtered_items),
            'total': 28699,  # Общее количество предметов в базе
            'items': filtered_items[offset:offset + limit],
            'pagination': {
                'limit': limit,
                'offset': offset,
                'next_offset': offset + limit if offset + limit < len(filtered_items) else None
            }
        }

        return JsonResponse(response_data)

    except Exception as e:
        return JsonResponse({
            'success': False,
            'error': str(e),
            'items': []
        }, status=500)


def logout_view(request):
    logout(request)
    if 'steam_data' in request.session:
        del request.session['steam_data']

    next_url = request.GET.get('next', 'home')
    return redirect(next_url)