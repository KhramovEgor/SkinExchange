import re
import os
import json
from urllib.parse import urlencode

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.urls import reverse
from django.views.decorators.http import require_GET


# =========================
# JSON DATA LOADER
# =========================

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CATEGORY_FILES = {
    "cases": "cases_items.json",
    "knives": "knives_items.json",
    "pistols": "pistols_items.json",
    "rifles": "rifles_items.json",
    "smg": "smg_items.json",
    "snipers": "snipers_items.json",
}


def load_items_from_json(category: str):
    file_name = CATEGORY_FILES.get(category)
    if not file_name:
        return []

    file_path = os.path.join(BASE_DIR, "main", file_name)
    print("Пробуем открыть JSON:", file_path)  # <-- добавь эту строку

    try:
        with open(file_path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print("Ошибка загрузки JSON:", e)
        return []



# =========================
# MAIN PAGE
# =========================

def home_view(request):
    category = request.GET.get("category")
    if not category or category not in CATEGORY_FILES:
        # редирект на страницу выбора категории или на дефолт
        category = "cases"  # можно сделать обязательный выбор
        # return redirect('/select-category/')  # если есть отдельная страница выбора

    items_data = load_items_from_json(category)
    steam_data = request.session.get('steam_data', {})

    context = {
        'user': request.user,
        'items_data': items_data,
        'steam_data': steam_data,
        'current_category': category,
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


# =========================
# API — только конкретная категория
# =========================

@require_GET
def get_items_by_category(request, category):
    if category not in CATEGORY_FILES:
        return JsonResponse({'success': False, 'error': 'Неверная категория'}, status=400)

    items = load_items_from_json(category)
    return JsonResponse({'success': True, 'count': len(items), 'items': items})


# =========================
# STEAM AUTH
# =========================

def steam_login(request):
    if request.user.is_authenticated:
        messages.info(request, "Вы уже авторизованы!")
        return redirect('home')

    next_url = request.GET.get('next') or request.POST.get('next') or 'home'
    request.session['login_next_url'] = next_url

    params = {
        'openid.ns': 'http://specs.openid.net/auth/2.0',
        'openid.mode': 'checkid_setup',
        'openid.return_to': request.build_absolute_uri(reverse('steam_auth:callback')),
        'openid.realm': request.build_absolute_uri('/'),
        'openid.identity': 'http://specs.openid.net/auth/2.0/identifier_select',
        'openid.claimed_id': 'http://specs.openid.net/auth/2.0/identifier_select',
    }

    auth_url = f"https://steamcommunity.com/openid/login?{urlencode(params)}"
    return redirect(auth_url)


def steam_callback(request):
    claimed_id = request.GET.get('openid.claimed_id', '')
    match = re.search(r'steamcommunity\.com/openid/id/(\d+)', claimed_id)

    if not match:
        messages.error(request, "Ошибка Steam ID")
        return redirect('home')

    steam_id = match.group(1)

    login(request, authenticate_steam_user(request, steam_id))
    request.session['steam_data'] = {'steam_id': steam_id}

    return redirect('home')


def authenticate_steam_user(request, steam_id):
    from .backends import SteamBackend
    backend = SteamBackend()
    return backend.authenticate(request, steam_id=steam_id)


# =========================
# INVENTORY
# =========================

@login_required
@require_GET
def get_steam_inventory(request):
    steam_id = "76561198080203313"
    appid = request.GET.get('appid', '730')

    items = fetch_steam_inventory(steam_id, appid)

    return JsonResponse({
        'success': True,
        'items': items[:100],
        'total': len(items)
    })


def fetch_steam_inventory(steam_id, appid, contextid='2'):
    url = f"https://steamcommunity.com/inventory/{steam_id}/{appid}/{contextid}"

    try:
        response = requests.get(url, timeout=15)
        data = response.json()

        if not data.get('success'):
            return []

        assets = data.get('assets', [])
        descriptions = data.get('descriptions', [])

        desc_map = {d['classid']: d for d in descriptions}

        items = []
        for asset in assets:
            desc = desc_map.get(asset['classid'])
            if not desc:
                continue

            items.append({
                'name': desc.get('name'),
                'market_hash_name': desc.get('market_hash_name'),
                'icon_url': desc.get('icon_url'),
                'tradable': desc.get('tradable') == 1,
            })

        return items

    except Exception:
        return []


# =========================
# PROFILE
# =========================

@login_required
def profile_view(request):
    steam_data = request.session.get('steam_data', {})

    return render(request, 'steam_auth/profile.html', {
        'user': request.user,
        'steam_data': steam_data,
        'page_title': 'Профиль'
    })


# =========================
# COMPARE PRICES
# =========================

@login_required
def compare_prices_view(request):
    category = request.GET.get("category", "cases")
    items_data = load_items_from_json(category)

    steam_data = request.session.get('steam_data', {})

    context = {
        'user': request.user,
        'steam_data': steam_data,
        'items_data': items_data,
        'page_title': 'Сравнение цен',
        'market_stats': {
            'total_items': len(items_data),
            'showing_items': len(items_data),
        }
    }

    return render(request, 'steam_auth/comparison_price.html', context)


# =========================
# API
# =========================

@require_GET
def get_market_data_api(request):
    category = request.GET.get("category", "cases")
    items = load_items_from_json(category)

    return JsonResponse({
        'success': True,
        'count': len(items),
        'items': items
    })


# =========================
# LOGOUT
# =========================

def logout_view(request):
    logout(request)
    request.session.flush()
    return redirect('home')
