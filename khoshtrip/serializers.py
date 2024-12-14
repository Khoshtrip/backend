from rest_framework import serializers
from .models import CustomerUser, ProviderUser, VerificationCode


class CustomerUserSerializer(serializers.ModelSerializer):
	verification_code = serializers.CharField(max_length=6)  # Add the verification_code field

	class Meta:
		model = CustomerUser
		fields = ['username', 'password', 'email', 'first_name', 'last_name', 'birth_date', 'mobile_number',
				  'id_number', 'verification_code']
		extra_kwargs = {'password': {'write_only': True}}

	def validate_verification_code(self, value):
		phone_number = self.initial_data.get('mobile_number')
		if not phone_number:
			raise serializers.ValidationError("Phone number is required to verify the code.")

		# Check if the verification code exists for the given phone number
		try:
			verification_code = VerificationCode.objects.get(mobile_number=phone_number, code=value)
		except VerificationCode.DoesNotExist:
			raise serializers.ValidationError("Invalid verification code.")

		# Check if the code has expired
		if verification_code.is_expired():
			raise serializers.ValidationError("The verification code has expired.")

		return value

	def create(self, validated_data):
		verification_code = validated_data.pop('verification_code')
		user = CustomerUser.objects.create_user(**validated_data)
		return user


class ProviderUserSerializer(serializers.ModelSerializer):
	verification_code = serializers.CharField(max_length=6)  # Add the verification_code field

	class Meta:
		model = ProviderUser
		fields = ['username', 'password', 'email', 'first_name', 'last_name', 'birth_date', 'mobile_number',
				  'id_number',
				  'business_name', 'business_address', 'website_url', 'verification_code']
		extra_kwargs = {'password': {'write_only': True}}

	def validate_verification_code(self, value):
		phone_number = self.initial_data.get('mobile_number')
		if not phone_number:
			raise serializers.ValidationError("Phone number is required to verify the code.")

		# Check if the verification code exists for the given phone number
		try:
			verification_code = VerificationCode.objects.get(mobile_number=phone_number, code=value)
		except VerificationCode.DoesNotExist:
			raise serializers.ValidationError("Invalid verification code.")

		# Check if the code has expired
		if verification_code.is_expired():
			raise serializers.ValidationError("The verification code has expired.")

		return value

	def create(self, validated_data):
		user = ProviderUser.objects.create_user(**validated_data)
		return user


class SendVerificationCodeSerializer(serializers.Serializer):
	phone_number = serializers.CharField(max_length=15)

	def validate_phone_number(self, value):
		# TODO: Add custom validation for phone number format if needed
		if not value.isdigit() or len(value) < 10:
			raise serializers.ValidationError("Invalid phone number.")
		return value


class VerifyCodeSerializer(serializers.Serializer):
	phone_number = serializers.CharField(max_length=15)
	code = serializers.CharField(max_length=6)
