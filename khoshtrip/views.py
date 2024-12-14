import random


from django.conf import settings
from rest_framework import views, status, permissions
from rest_framework.response import Response

from .models import VerificationCode
from .serializers import CustomerUserSerializer, ProviderUserSerializer, SendVerificationCodeSerializer, VerifyCodeSerializer

from django.utils.timezone import now
from datetime import timedelta


class RegisterCustomerUserView(views.APIView):
    def post(self, request):
        serializer = CustomerUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Buyer registered successfully.",
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "error",
            "message": "Invalid or missing input fields.",
            "code": "VALIDATION_ERROR",
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)


class RegisterProviderUserView(views.APIView):
    def post(self, request):
        serializer = ProviderUserSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Provider registered successfully.",
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "error",
            "message": "Invalid or missing input fields.",
            "code": "VALIDATION_ERROR",
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)



class SendVerificationCodeView(views.APIView):
    # Allow unauthenticated access
    authentication_classes = []  # Disable authentication
    permission_classes = [permissions.AllowAny]  # Allow access to anyone

    def post(self, request):
        serializer = SendVerificationCodeSerializer(data=request.data)
        if serializer.is_valid():
            print("hello", request.data)
            phone_number = serializer.validated_data['phone_number']

            # Generate a random 6-digit verification code
            verification_code = f"{random.randint(100000, 999999)}"

            # Save or update the verification code in the database
            expiration_minutes = getattr(settings, "VERIFICATION_CODE_EXPIRATION_MINUTES", 5)
            expiration = now() + timedelta(minutes=expiration_minutes)

            VerificationCode.objects.update_or_create(
                mobile_number=phone_number,
                defaults={'code': verification_code, "expiration": expiration},
            )

            # Simulate sending the verification code (e.g., via SMS)
            # TODO: Send a real SMS

            return Response({
                "status": "success",
                "message": "Verification code sent successfully."
            }, status=status.HTTP_200_OK)

        # Return validation errors
        return Response({
            "status": "error",
            "message": "Invalid phone number.",
            "code": "INVALID_CONTACT"
        }, status=status.HTTP_400_BAD_REQUEST)


class VerifyCodeView(views.APIView):
    authentication_classes = []  # Disable authentication
    permission_classes = [permissions.AllowAny]  # Allow access to anyone

    def post(self, request):
        # Initialize the serializer with the request data
        serializer = VerifyCodeSerializer(data=request.data)

        if serializer.is_valid():
            # Extract phone_number and code from validated data
            phone_number = serializer.validated_data['phone_number']
            code = serializer.validated_data['code']

            # Retrieve the verification code record from the database
            try:
                verification_code = VerificationCode.objects.get(mobile_number=phone_number, code=code)
            except VerificationCode.DoesNotExist:
                return Response({
                    "status": "error",
                    "message": "Invalid or expired verification code.",
                    "code": "INVALID_CODE"
                }, status=status.HTTP_400_BAD_REQUEST)

            # Check if the code is expired
            if verification_code.is_expired():
                return Response({
                    "status": "error",
                    "message": "Invalid or expired verification code.",
                    "code": "EXPIRED_CODE"
                }, status=status.HTTP_400_BAD_REQUEST)

            # If the code is valid and not expired, return success
            return Response({
                "status": "success",
                "message": "Verification successful.",
                "phone_number": phone_number
            }, status=status.HTTP_200_OK)

        # If the serializer is invalid, return validation errors
        return Response({
            "status": "error",
            "message": "Invalid input data.",
            "code": "VALIDATION_ERROR"
        }, status=status.HTTP_400_BAD_REQUEST)
