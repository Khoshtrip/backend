from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated
from authorization.permissions import IsProvider

# Create your views here.

class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated, IsProvider]

    def post(self, request):
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            product = serializer.save(provider=request.user.provider_profile)
            return Response({
                'status': 'success',
                'message': 'Product created successfully.'
            }, status=status.HTTP_201_CREATED)
        return Response({
            'status': 'error',
            'message': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
