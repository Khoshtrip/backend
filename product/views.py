from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated
from authorization.permissions import IsProvider
from utils.exceptions import ValidationError, PermissionError
from utils.error_codes import ErrorCodes
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .models import Product
from .pagination import CustomPagination
from .filters import ProductFilter

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

class ProductListView(ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'summary', 'description']
    filterset_class = ProductFilter
    pagination_class = CustomPagination

    def get_queryset(self):
        user = self.request.user
        return Product.objects.filter(provider=user.provider_profile)
