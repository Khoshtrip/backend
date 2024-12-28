from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .models import VerificationCode, BaseUser, ProviderProfile
from .serializers import (
    SendVerificationCodeSerializer,
    VerifyCodeSerializer,
    RegisterCustomerSerializer,
    RegisterProviderSerializer,
    LoginSerializer,
    LogoutSerializer,
    RefreshTokenSerializer,
    UserDetailSerializer,
)
import random
from utils.exceptions import ValidationError, ResourceNotFoundError
from utils.error_codes import ErrorCodes

class SendVerificationCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = SendVerificationCodeSerializer(data=request.data)
            if not serializer.is_valid():
                raise ValidationError({
                    'message': 'Invalid input data',
                    'code': ErrorCodes.INVALID_PHONE,
                    'errors': serializer.errors
                })

            phone_number = serializer.validated_data['phone_number']
            if BaseUser.objects.filter(phone_number=phone_number).exists():
                raise ValidationError({
                    'message': 'User with this phone number already exists',
                    'code': ErrorCodes.USER_EXISTS
                })

            code = str(random.randint(100000, 999999))
            print(f"Sending code {code}")  # For development
            VerificationCode.objects.create(phone_number=phone_number, code=code)

            return Response({
                'status': 'success',
                'message': 'Verification code sent successfully.'
            })

        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(str(e))


class VerifyCodeView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        try:
            serializer = VerifyCodeSerializer(data=request.data)
            if not serializer.is_valid():
                raise ValidationError({
                    'message': 'Invalid input data',
                    'code': ErrorCodes.INVALID_INPUT,
                    'errors': serializer.errors
                })

            phone_number = serializer.validated_data['phone_number']
            code = serializer.validated_data['code']

            try:
                verification_code = VerificationCode.objects.get(
                    phone_number=phone_number, code=code, is_used=False
                )
                verification_code.is_used = True
                verification_code.save()

                return Response({
                    'status': 'success',
                    'message': 'Verification successful.',
                    'data': {'phone_number': phone_number}
                })

            except VerificationCode.DoesNotExist:
                raise ValidationError({
                    'message': 'Invalid or expired verification code',
                    'code': ErrorCodes.INVALID_CODE
                })

        except Exception as e:
            if isinstance(e, ValidationError):
                raise e
            raise ValidationError(str(e))


class RegisterBuyerView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterCustomerSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success', 'message': 'Buyer registered successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RegisterProviderView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegisterProviderSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({'status': 'success', 'message': 'Provider registered successfully.'})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        try:
            serializer = LoginSerializer(data=request.data)
            if not serializer.is_valid():
                raise AuthenticationError({
                    'message': 'Invalid credentials',
                    'code': ErrorCodes.INVALID_CREDENTIALS,
                    'errors': serializer.errors
                })

            phone_number = serializer.validated_data['phone_number']
            password = serializer.validated_data['password']

            try:
                user = BaseUser.objects.get(phone_number=phone_number)
                if not user.check_password(password):
                    raise AuthenticationError({
                        'message': 'Invalid credentials',
                        'code': ErrorCodes.INVALID_CREDENTIALS
                    })

                tokens = RefreshToken.for_user(user)
                return Response({
                    'status': 'success',
                    'data': {
                        'access': str(tokens.access_token),
                        'refresh': str(tokens)
                    }
                })

            except BaseUser.DoesNotExist:
                raise AuthenticationError({
                    'message': 'Invalid credentials',
                    'code': ErrorCodes.INVALID_CREDENTIALS
                })

        except Exception as e:
            if isinstance(e, AuthenticationError):
                raise e
            raise AuthenticationError(str(e))


class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = LogoutSerializer(data=request.data)
        if serializer.is_valid():
            refresh_token = serializer.validated_data['refresh']
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
                return Response({'status': 'success', 'message': 'Logged out successfully.'})
            except Exception:
                return Response({'status': 'error', 'message': 'Invalid or expired refresh token.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(TokenRefreshView):
    serializer_class = RefreshTokenSerializer


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            user = request.user
            base_data = {
                "first_name": user.first_name,
                "last_name": user.last_name,
                "phone_number": user.phone_number,
                "email": user.email,
                "role": user.role,
                "national_id": user.national_id,
                "date_joined": user.date_joined,
            }

            if user.role == 'provider':
                try:
                    provider_profile = user.provider_profile
                    base_data.update({
                        "business_name": provider_profile.business_name,
                        "business_address": provider_profile.business_address,
                        "business_contact": provider_profile.business_contact,
                        "website_url": provider_profile.website_url,
                    })
                except ProviderProfile.DoesNotExist:
                    raise ResourceNotFoundError({
                        'message': 'Provider profile not found',
                        'code': ErrorCodes.NOT_FOUND
                    })

            return Response({
                'status': 'success',
                'data': base_data
            })

        except Exception as e:
            if isinstance(e, (ResourceNotFoundError, ValidationError)):
                raise e
            raise ValidationError(str(e))
