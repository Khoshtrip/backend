from rest_framework import serializers
from .models import CustomerUser, ProviderUser


class CustomerUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomerUser
        fields = ['username', 'password', 'first_name', 'last_name', 'birth_date', 'mobile_number', 'id_number',
                  'email_address']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = CustomerUser.objects.create_user(**validated_data)
        return user


class ProviderUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProviderUser
        fields = ['username', 'password', 'first_name', 'last_name', 'birth_date', 'mobile_number', 'id_number',
                  'email_address', 'business_name', 'business_address', 'business_contact', 'website_url']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = ProviderUser.objects.create_user(**validated_data)
        return user
