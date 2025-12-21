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

# В начало views.py добавьте:
from django.template.defaulttags import register


@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)


@register.filter
def format_price(value):
    if isinstance(value, (int, float)):
        return f"${value:.2f}"
    return value


@register.filter
def format_change(value):
    if isinstance(value, (int, float)):
        sign = '+' if value >= 0 else ''
        return f"{sign}{value:.1f}%"
    return value


@register.filter
def get_change_class(value):
    if isinstance(value, (int, float)):
        return 'positive' if value >= 0 else 'negative'
    return ''


@register.filter
def get_wear_display_name(wear):
    wear_names = {
        'factory-new': 'Примо с завода',
        'minimal-wear': 'Минимальный износ',
        'field-tested': 'Полевые испытания',
        'well-worn': 'Сильно изношено',
        'battle-scarred': 'С боевыми следами'
    }
    return wear_names.get(wear, wear)


@register.filter
def create_rating_stars(rating):
    full_stars = int(rating)
    has_half_star = rating - full_stars >= 0.5
    empty_stars = 5 - full_stars - (1 if has_half_star else 0)

    stars = ''
    for _ in range(full_stars):
        stars += '<i class="fas fa-star star"></i>'
    if has_half_star:
        stars += '<i class="fas fa-star-half-alt star"></i>'
    for _ in range(empty_stars):
        stars += '<i class="far fa-star star empty"></i>'

    return stars

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

    # Данные для популярных скинов (заглушки)
    popular_skins = [
        {"change": "21.13", "weapon": "P2000", "name": "Императорский дракон FN", "price": "$49.72"},
        {"change": "17.01", "weapon": "StatTrak™ Фальшион", "name": "Ночь FT", "price": "$184.66"},
        {"change": "18.29", "weapon": "AWP", "name": "Элитное снаряжение FT", "price": "$40.91"},
        {"change": "16.39", "weapon": "Автомат «Галиль»", "name": "ОСТОРОЖНО! MW", "price": "$85.23"},
    ]

    steam_data = request.session.get('steam_data', {})

    context = {
        'user': request.user,
        'items_data': items_data,
        'popular_skins': popular_skins,
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
        # Получаем Steam ID из сессии или из данных пользователя
        steam_data = request.session.get('steam_data', {})
        steam_id = steam_data.get('steam_id')

        if not steam_id:
            # Пытаемся получить Steam ID из модели пользователя
            from .models import SteamUser
            steam_user = SteamUser.objects.filter(user=request.user).first()
            if steam_user:
                steam_id = steam_user.steam_id

        if not steam_id:
            return JsonResponse({
                'error': 'Steam ID не найден. Пожалуйста, войдите заново.',
                'items': []
            }, status=400)

        # Получаем appid из параметров запроса
        appid = request.GET.get('appid', '730')  # По умолчанию CS:GO

        items = fetch_steam_inventory(steam_id, appid, '2')

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
            'error': f'Внутренняя ошибка сервера: {str(e)}',
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

    # Если Steam ID не сохранился в сессии, получаем его из данных пользователя
    if not steam_data.get('steam_id'):
        try:
            from .models import SteamUser
            steam_user = SteamUser.objects.filter(user=request.user).first()
            if steam_user:
                steam_data['steam_id'] = steam_user.steam_id
        except Exception:
            pass

    # Получаем дополнительную информацию о профиле Steam через API
    if steam_data.get('steam_id'):
        try:
            api_key = getattr(settings, 'STEAM_API_KEY', '')
            if api_key:
                # Получаем детальную информацию о профиле
                profile_info = get_steam_user_info(steam_data['steam_id'], api_key)
                if profile_info:
                    # Обновляем steam_data новой информацией
                    steam_data.update(profile_info)

                    # Сохраняем обновленные данные в сессии
                    request.session['steam_data'] = steam_data
        except Exception as e:
            print(f"Ошибка получения данных Steam: {e}")

    user_stats = {
        'items_count': 0,
        'trades_count': 0,
        'last_update': 'Сегодня',
        'inventory_value': '$0'
    }

    # Пытаемся получить данные об инвентаре
    try:
        steam_id = steam_data.get('steam_id', steam_data['steam_id'])
        inventory_items = fetch_steam_inventory(steam_id, '730', '2')
        if inventory_items:
            user_stats['items_count'] = len(inventory_items)
            user_stats['trades_count'] = len([i for i in inventory_items if i.get('tradable')])
    except Exception:
        pass

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


# views.py
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
import json
from django.views.decorators.http import require_GET
import requests
from django.conf import settings


def skin_detail_view(request, skin_name, wear=None):
    """
    View для отображения детальной страницы скина
    """
    # Получаем данные о скине из базы данных или API
    # В реальном приложении здесь будет запрос к базе данных

    # Пример данных для тестирования
    context = {
        'skin': {
            'name': 'МР9 | Hydra',
            'weapon': 'MP9',
            'collection': 'Hydra',
            'rarity': 'Засекреченное',
            'description': 'Производимый в Швейцарии передовой пистолет-пулемёт МР9 – это эргономичное полимерное оружие, используемое частными охранными структурами по всему миру. Он был окрашен в гидравлическую тематику с использованием металлических красок и аэрографии. Коллекция «Гидра».',
            'extended_description': 'Этот уникальный дизайн был создан талантливым художником и является частью ограниченной серии. Скины коллекции «Гидра» известны своей детализацией и яркими цветами, что делает их популярными среди коллекционеров.',
            'image_url': 'https://steamcommunity-a.akamaihd.net/economy/image/-9a81dlWLwJ2UUGcVs_nsVtzdOEdtWwKGZZLQHTxDZ7I56KU0Zwwo4NUX4oFJZEHLbXU5A1PIYQh5hlcX0nvUOGsx8DdQBJjIAVHubSaIAlp1fb3ejx95-GJlY6OhPLLNqnVkWkJ6cQn2rCRoIql2A3i-0E5ZjqhJ9ScI1BrYlzW81fswe650Z-8u8vPnyBk7nMi5CrD30vgUxMdi3oYJ7WJGAvjY9fM-FS4FA/360fx360f',
            'wears': {
                'factory-new': {
                    'price': 118.51,
                    'change': 2.3,
                    'available': True
                },
                'minimal-wear': {
                    'price': 30.44,
                    'change': -1.2,
                    'available': True
                },
                'field-tested': {
                    'price': 11.85,
                    'change': 0.8,
                    'available': True
                },
                'well-worn': {
                    'price': 7.32,
                    'change': 3.1,
                    'available': True
                },
                'battle-scarred': {
                    'price': 5.81,
                    'change': -0.5,
                    'available': True
                }
            },
            'rating': 4.5,
            'votes': 872,
            'weekly_change': 50.63,
            'weekly_percent': 74.6,
            'monthly_change': 69.50,
            'monthly_percent': 141.8,
            'current_price': 118.51
        },
        'price_history': {
            'current': 118.51,
            'week_low': 60.63,
            'week_high': 76.05,
            'month_low': 38.02,
            'month_high': 60.63,
            'three_month_low': 29.47,
            'three_month_high': 48.52,
            'all_time_low': 9.58,
            'all_time_high': 124.83
        },
        'selected_wear': wear if wear else 'factory-new'
    }

    return render(request, 'steam_auth/skin_detail.html', context)


@require_GET
def get_skin_data_api(request, skin_name):
    """
    API для получения данных о скине
    """
    # Здесь будет логика получения данных из базы или внешнего API
    # Пока возвращаем тестовые данные

    data = {
        'name': skin_name,
        'weapon': 'MP9',
        'collection': 'Hydra',
        'rarity': 'Classified',
        'description': 'Detailed description of the skin...',
        'wears': {
            'factory-new': {'price': 118.51, 'change': 2.3},
            'minimal-wear': {'price': 30.44, 'change': -1.2},
            'field-tested': {'price': 11.85, 'change': 0.8},
            'well-worn': {'price': 7.32, 'change': 3.1},
            'battle-scarred': {'price': 5.81, 'change': -0.5}
        }
    }

    return JsonResponse(data)


@require_GET
def get_skin_prices_api(request, skin_name):
    """
    API для получения цен скина по разным платформам
    """
    wear = request.GET.get('wear', 'factory-new')

    # Тестовые данные
    data = {
        'skin': skin_name,
        'wear': wear,
        'prices': [
            {
                'platform': 'Steam Market',
                'icon': 'https://steamcommunity.com/favicon.ico',
                'price': 118.51,
                'date': 'Today, 15:42',
                'wear': 'FN'
            },
            {
                'platform': 'Skinport',
                'icon': 'https://skinport.com/favicon.ico',
                'price': 115.20,
                'date': 'Today, 14:30',
                'wear': 'FN'
            },
            {
                'platform': 'DMarket',
                'icon': 'https://dmarket.com/favicon.ico',
                'price': 116.85,
                'date': 'Today, 13:15',
                'wear': 'FN'
            }
        ]
    }

    return JsonResponse(data)


@require_GET
def get_skin_history_api(request, skin_name):
    """
    API для получения истории цен скина
    """
    period = request.GET.get('period', '7d')
    wear = request.GET.get('wear', 'factory-new')

    # Генерация тестовых данных
    if period == '7d':
        data = [
            {'date': '2024-01-01', 'price': 79.09},
            {'date': '2024-01-02', 'price': 92.44},
            {'date': '2024-01-03', 'price': 76.79},
            {'date': '2024-01-04', 'price': 76.60},
            {'date': '2024-01-05', 'price': 79.31},
            {'date': '2024-01-06', 'price': 86.03},
            {'date': '2024-01-07', 'price': 85.72}
        ]
    elif period == '30d':
        data = []
        for i in range(30, 0, -1):
            data.append({
                'date': f'2024-01-{i:02d}',
                'price': 60 + (i * 0.5) + (i % 3)
            })
    else:
        data = [
            {'date': '2023-10', 'price': 29.47},
            {'date': '2023-11', 'price': 32.15},
            {'date': '2023-12', 'price': 38.02},
            {'date': '2024-01', 'price': 42.50},
            {'date': '2024-02', 'price': 48.52},
            {'date': '2024-03', 'price': 52.30},
            {'date': '2024-04', 'price': 60.63},
            {'date': '2024-05', 'price': 65.80},
            {'date': '2024-06', 'price': 70.45},
            {'date': '2024-07', 'price': 85.18},
            {'date': '2024-08', 'price': 95.60},
            {'date': '2024-09', 'price': 118.51}
        ]

    return JsonResponse({'period': period, 'data': data})


def logout_view(request):
    logout(request)
    if 'steam_data' in request.session:
        del request.session['steam_data']

    next_url = request.GET.get('next', 'home')
    return redirect(next_url)


def pricing_view(request):
    """Страница тарифных планов"""
    steam_data = request.session.get('steam_data', {})

    # Проверяем текущую подписку пользователя
    user_subscription = {
        'plan': 'free',  # free, standard, pro, business
        'expires_at': None,
        'trial_days_left': 0
    }

    # Если пользователь авторизован, можно проверить его подписку в базе данных
    if request.user.is_authenticated:
        try:
            from .models import UserSubscription
            subscription = UserSubscription.objects.filter(user=request.user).first()
            if subscription:
                user_subscription = {
                    'plan': subscription.plan_type,
                    'expires_at': subscription.expires_at,
                    'trial_days_left': subscription.trial_days_left
                }
        except:
            pass

    context = {
        'user': request.user,
        'steam_data': steam_data,
        'user_subscription': user_subscription,
        'page_title': 'Тарифные планы - CS Market Analytics',
    }

    return render(request, 'steam_auth/pricing.html', context)