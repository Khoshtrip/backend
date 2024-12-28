from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated
from authorization.permissions import IsProvider
from utils.exceptions import ValidationError, PermissionError
from utils.error_codes import ErrorCodes

# Create your views here.

class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated, IsProvider]

    def post(self, request):
        try:
            serializer = ProductSerializer(data=request.data)
            if not serializer.is_valid():
                raise ValidationError({
                    'message': 'Invalid product data',
                    'code': ErrorCodes.INVALID_INPUT,
                    'errors': serializer.errors
                })

            product = serializer.save(provider=request.user.provider_profile)
            return Response({
                'status': 'success',
                'message': 'Product created successfully.',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            if isinstance(e, (ValidationError, PermissionError)):
                raise e
            raise ValidationError(str(e))
