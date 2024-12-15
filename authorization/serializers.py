from rest_framework import serializers
from .models import BaseUser, ProviderProfile

class SendVerificationCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)

class VerifyCodeSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    code = serializers.CharField(max_length=6)

class RegisterCustomerSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = BaseUser
        fields = [
            'first_name', 'last_name', 'phone_number', 'email', 'national_id', 'password'
        ]

    def create(self, validated_data):
        validated_data['role'] = 'customer'
        password = validated_data.pop('password')
        user = BaseUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()
        return user


class RegisterProviderSerializer(serializers.Serializer):
    first_name = serializers.CharField(required=False, allow_blank=True)
    last_name = serializers.CharField(required=False, allow_blank=True)
    phone_number = serializers.CharField(max_length=15)
    email = serializers.EmailField(required=False, allow_null=True)
    national_id = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    password = serializers.CharField(write_only=True)
    business_name = serializers.CharField(max_length=100)
    business_address = serializers.CharField(max_length=255, required=False, allow_blank=True)
    business_contact = serializers.CharField(max_length=15)
    website_url = serializers.URLField(required=False, allow_blank=True)

    def create(self, validated_data):
        password = validated_data.pop('password')
        business_name = validated_data.pop('business_name')
        business_address = validated_data.pop('business_address', None)
        business_contact = validated_data.pop('business_contact')
        website_url = validated_data.pop('website_url', None)

        validated_data['role'] = 'provider'
        user = BaseUser.objects.create_user(**validated_data)
        user.set_password(password)
        user.save()

        ProviderProfile.objects.create(
            user=user,
            business_name=business_name,
            business_address=business_address,
            business_contact=business_contact,
            website_url=website_url
        )

        return user


class LoginSerializer(serializers.Serializer):
    phone_number = serializers.CharField()
    password = serializers.CharField()


class LogoutSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class RefreshTokenSerializer(serializers.Serializer):
    refresh = serializers.CharField()


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = BaseUser
        fields = [
            'id', 'phone_number', 'email', 'role', 'date_joined', 
            'first_name', 'last_name', 'national_id'
        ]
