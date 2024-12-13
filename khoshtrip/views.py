from rest_framework import views, status
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import CustomerUserSerializer, ProviderUserSerializer


class RegisterCustomerUserView(views.APIView):
    def post(self, request):
        serializer = CustomerUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "status": "success",
                "message": "Buyer registered successfully.",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
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
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({
                "status": "success",
                "message": "Provider registered successfully.",
                "refresh": str(refresh),
                "access": str(refresh.access_token),
            }, status=status.HTTP_200_OK)
        return Response({
            "status": "error",
            "message": "Invalid or missing input fields.",
            "code": "VALIDATION_ERROR",
            "errors": serializer.errors,
        }, status=status.HTTP_400_BAD_REQUEST)
