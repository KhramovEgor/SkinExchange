from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from .models import UserSkin

@login_required
def user_inventory(request):
    # Заглушка пока нет реальных данных
    return JsonResponse({
        'user': request.user.username,
        'inventory': [],
        'message': 'Инвентарь будет доступен после привязки Steam'
    })