from rest_framework import serializers
from .models import Product

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'summary', 'description', 'price', 
            'stock', 'category', 'image', 'isActive', 
            'created_at', 'updated_at'
        ]

    def get_image(self, obj):
        return obj.images[0] if obj.images else None 