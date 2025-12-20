from rest_framework import serializers
from .models import Skin

class SkinSerializer(serializers.ModelSerializer):
    rarity_display = serializers.CharField(source='get_rarity_display', read_only=True)
    
    class Meta:
        model = Skin
        fields = [
            'id', 
            'name', 
            'skin_type',  # ВАЖНО: skin_type, а не type!
            'rarity',
            'rarity_display',
            'image_url', 
            'price', 
            'metadata'
        ]