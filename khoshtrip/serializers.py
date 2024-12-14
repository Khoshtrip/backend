from rest_framework import serializers
from .models import CustomerUser, ProviderUser


class CustomerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerUser
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'birth_date', 'mobile_number', 'id_number']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomerUser.objects.create_user(**validated_data)
        return user


class ProviderUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderUser
        fields = ['username', 'password', 'email', 'first_name', 'last_name', 'birth_date', 'mobile_number', 'id_number',
                  'business_name', 'business_address', 'website_url']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = ProviderUser.objects.create_user(**validated_data)
        return user
