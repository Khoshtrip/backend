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
            'available_units', 'rating', 'ratings_count'
        ]

class TripPackageSerializer(serializers.ModelSerializer):
    class Meta:
        model = TripPackage
        fields = [
            'id', 'name', 'photos', 'flight', 'hotel',
            'activities', 'price', 'start_date', 'end_date',
            'available_units', 'published', 'description',
            'created_at', 'updated_at', 'rating', 'ratings_count'
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
    
class TripPackageDetailSerializer(serializers.ModelSerializer):
    flight = ProductSerializer(read_only=True)
    hotel = ProductSerializer(read_only=True)
    activities = ProductSerializer(many=True, read_only=True)

    class Meta:
        model = TripPackage
        fields = [
            'id', 'name', 'photos', 'flight', 'hotel',
            'activities', 'price', 'start_date', 'end_date',
            'available_units', 'published', 'description',
            'created_at', 'updated_at', 'rating', 'ratings_count'
        ]
        read_only_fields = ['created_at', 'updated_at']
        
class PurchasePackageSerializer(serializers.Serializer):
    card_number = serializers.CharField(max_length=16)
    expiration_date = serializers.CharField(max_length=20, required=False)
    expiration_date_month = serializers.CharField(max_length=2, required=False)
    expiration_date_year = serializers.CharField(max_length=20, required=False)
    cvv2 = serializers.CharField(max_length=4)
    pin = serializers.CharField(max_length=4)
    quantity = serializers.IntegerField(default=1, min_value=1)

    def validate(self, data):
        # Validate card number (mock validation)
        if not data['card_number'].isdigit() or len(data['card_number']) != 16:
            raise serializers.ValidationError({'card_number': 'Invalid card number'})

        # Handle both expiration date formats
        if 'expiration_date' in data:
            try:
                # Try to split by '/'
                parts = data['expiration_date'].split('/')
                if len(parts) == 2:
                    month, year = parts
                    if not (1 <= int(month) <= 12):
                        raise serializers.ValidationError({'expiration_date': 'Invalid month in expiration date'})
                else:
                    # If not in MM/YY format, just accept it for now (mock validation)
                    pass
            except (ValueError, IndexError):
                # If there's an error parsing, just accept it for now (mock validation)
                pass
        elif 'expiration_date_month' in data and 'expiration_date_year' in data:
            # If separate month and year are provided, validate month
            try:
                month = data['expiration_date_month']
                if not (1 <= int(month) <= 12):
                    raise serializers.ValidationError({'expiration_date_month': 'Invalid month'})
                
                # Combine into expiration_date for consistency
                data['expiration_date'] = f"{month}/{data['expiration_date_year']}"
            except (ValueError, TypeError):
                # If month is not a valid number, just accept it for now (mock validation)
                data['expiration_date'] = f"{data['expiration_date_month']}/{data['expiration_date_year']}"
        else:
            raise serializers.ValidationError({'expiration_date': 'Either expiration_date or both expiration_date_month and expiration_date_year must be provided'})

        # Validate CVV2 (mock validation)
        if not data['cvv2'].isdigit() or len(data['cvv2']) not in [3, 4]:
            raise serializers.ValidationError({'cvv2': 'Invalid CVV2'})

        # Validate PIN (mock validation)
        if not data['pin'].isdigit() or len(data['pin']) != 4:
            raise serializers.ValidationError({'pin': 'Invalid PIN'})

        # Validate quantity
        if data['quantity'] < 1:
            raise serializers.ValidationError({'quantity': 'Quantity must be at least 1'})

        return data
