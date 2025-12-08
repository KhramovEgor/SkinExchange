# auth_app/views.py
from django.http import JsonResponse

def steam_login(request):
    """Заглушка для Steam OAuth"""
    return JsonResponse({
        'status': 'not_implemented',
        'message': 'Steam OAuth will be implemented in Sprint 2',
        'stub': 'Redirect to Steam would happen here'
    })

def steam_callback(request):
    """Заглушка для callback"""
    return JsonResponse({
        'status': 'not_implemented',
        'message': 'Steam callback will be implemented in Sprint 2',
        'stub': 'User authentication would happen here'
    })