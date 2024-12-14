import random

from rest_framework import views, status, permissions
from rest_framework.response import Response

from .models import VerificationCode
from .serializers import CustomerUserSerializer, ProviderUserSerializer, SendVerificationCodeSerializer


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
            phone_number = serializer.validated_data['phone_number']

            # Generate a random 6-digit verification code
            verification_code = f"{random.randint(100000, 999999)}"

            # Save or update the verification code in the database
            VerificationCode.objects.update_or_create(
                mobile_number=phone_number,
                defaults={'code': verification_code},
            )

            # Simulate sending the verification code (e.g., via SMS)
            # TODO: Send a real SMS
            print(f"Sending verification code {verification_code} to {phone_number}")

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

