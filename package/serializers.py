from rest_framework import serializers
from .models import TripPackage
from product.models import Product, Image

class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'name', 'summary', 'description', 'price', 'category']

class TripPackageListSerializer(serializers.ModelSerializer):
    flight = ProductSerializer(read_only=True)
    hotel = ProductSerializer(read_only=True)
    activities = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = TripPackage
        fields = [
            'id', 'name', 'photos', 'flight', 'hotel',
            'activities', 'price', 'start_date', 'end_date', 'published',
            'available_units'
        ]

class TripPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripPackage
        fields = [
            'id', 'name', 'photos', 'flight', 'hotel',
            'activities', 'price', 'start_date', 'end_date',
            'available_units', 'published', 'description',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['created_at', 'updated_at']

    def validate(self, data):
        # Validate start_date is before end_date
        if data.get('start_date') and data.get('end_date'):
            if data['start_date'] >= data['end_date']:
                raise serializers.ValidationError({
                    'end_date': 'End date must be after start date'
                })

        # Validate flight is a flight product
        if data.get('flight') and data['flight'].category != 'flight':
            raise serializers.ValidationError({
                'flight': 'Selected product must be a flight'
            })

        # Validate hotel is a hotel product
        if data.get('hotel') and data['hotel'].category != 'hotel':
            raise serializers.ValidationError({
                'hotel': 'Selected product must be a hotel'
            })

        # Validate activities are tourism or restaurant products
        if 'activities' in data:
            for activity in data['activities']:
                if activity.category not in ['tourism', 'restaurant']:
                    raise serializers.ValidationError({
                        'activities': 'Activities must be tourism or restaurant products'
                    })

        return data

