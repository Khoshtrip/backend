from rest_framework import serializers
from .models import Product
from rest_framework import serializers
from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'file', 'uploaded_at']

class ProductSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'summary', 'description', 'price', 
            'discount', 'stock', 'category', 'image', 'isActive', 
            'created_at', 'updated_at'
        ]

    def get_image(self, obj):
        return obj.images[0] if obj.images else None 