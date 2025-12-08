from django.http import JsonResponse
from .models import Skin

def skin_list(request):
    skins = Skin.objects.all()[:20]  # первые 20 скинов
    data = [
        {
            'id': skin.id,
            'name': skin.name,
            'type': skin.skin_type,
            'rarity': skin.rarity,
            'price': str(skin.price),
            'image_url': skin.image_url,
        }
        for skin in skins
    ]
    return JsonResponse({'skins': data})