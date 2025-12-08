from django.contrib import admin
from django.urls import path, include
from django.http import JsonResponse

def home(request):
    return JsonResponse({
        'project': 'SkinTrade Platform',
        'version': '1.0',
        'sprint': 1,
        'endpoints': {
            'admin': '/admin/',
            'auth': '/auth/',
            'catalog': '/catalog/',
            'inventory': '/inventory/'
        }
    })

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('auth/', include('auth_app.urls')),
    path('catalog/', include('catalog.urls')),
    path('inventory/', include('inventory.urls')),
]