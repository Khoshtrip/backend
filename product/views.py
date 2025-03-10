from django.db import transaction
from django.db.models import F
from django.http import FileResponse, Http404
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import status
from rest_framework.exceptions import PermissionDenied
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListAPIView
from rest_framework.parsers import MultiPartParser
from rest_framework.permissions import AllowAny
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from authorization.permissions import IsPackageMaker
from authorization.permissions import IsProvider
from utils.cache_monitoring import MonitoredCacheMixin
from utils.error_codes import ErrorCodes
from utils.exceptions import ValidationError, PermissionError, ResourceNotFoundError
from .filters import ProductFilter
from .models import Image
from .models import Product
from .pagination import CustomPagination
from .serializers import ProductSerializer


class ImageUploadView(APIView):
    parser_classes = [MultiPartParser]

    def post(self, request, *args, **kwargs):
        file = request.data.get('file')
        if not file:
            return Response(
                {"status": "error", "message": "No file provided."},
                status=status.HTTP_400_BAD_REQUEST
            )
        # image = Image.objects.create(file=file, uploader=request.user)
        image = Image.objects.create(file=file)

        return Response(
            {"status": "success",
                "message": "Here is your image :)",
             "imageId": image.id},
            status=status.HTTP_200_OK
        )

class ImageDeleteView(APIView):
    def delete(self, request, imageId, *args, **kwargs):
        try:
            # image = Image.objects.get(id=imageId, uploader=request.user)
            image = Image.objects.get(id=imageId)

        except Image.DoesNotExist:
            return Response(
                {"status": "error", "message": "Image not found.","code": "RES_001",},
                status=status.HTTP_404_NOT_FOUND
            )
        image.file.delete()
        image.delete()
        return Response(
            {"status": "success", "message": "Image deleted successfully."},
            status=status.HTTP_200_OK
        )

class ImageDownloadView(APIView):
    permission_classes = [AllowAny]
    
    def get(self, request, imageId, *args, **kwargs):
        try:
            image = Image.objects.get(id=imageId)
        except Image.DoesNotExist:
            return Response(
                {"status": "error",
                 "message": "Image not found.",
                 "code": "RES_001",
                 },
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Open the image file
        file = image.file.open()
        return FileResponse(file, content_type="image/jpeg")


# Create your views here.

class ProductCreateView(APIView):
    permission_classes = [IsAuthenticated, IsProvider]

    def post(self, request):
        try:
            serializer = ProductSerializer(data=request.data)
            if not serializer.is_valid():
                return Response({
                    'status': 'error',
                    'message': 'Invalid product data',
                    'code': ErrorCodes.INVALID_INPUT,
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

            product = serializer.save(provider=request.user.provider_profile)
            return Response({
                'status': 'success',
                'message': 'Product created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            if isinstance(e, (ValidationError, PermissionError)):
                raise e
            raise ValidationError(str(e))

class ProductListView(MonitoredCacheMixin, ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'summary', 'description']
    filterset_class = ProductFilter
    pagination_class = CustomPagination
    cache_timeout = 60 * 5  # 5 minutes
    cache_key_prefix = 'product_list'
    
    def get_cache_key_prefix(self):
        """
        Override the cache key prefix to include the user ID to ensure
        each user has their own cache.
        """
        user_id = self.request.user.id if self.request.user and self.request.user.is_authenticated else 'anonymous'
        return f"{self.cache_key_prefix}_{user_id}"
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    def get_queryset(self):
        if hasattr(self.request.user, 'provider_profile'):
            queryset = Product.objects.filter(provider=self.request.user.provider_profile)
            
            is_active_param = self.request.query_params.get('isActive')
            if is_active_param is None:
                queryset = queryset.filter(isActive=True)
            
            return queryset
        return Product.objects.none()

class ProductDetailsView(MonitoredCacheMixin, APIView):
    cache_timeout = 60 * 5  # 5 minutes
    cache_key_prefix = 'product_detail'
    
    def get_cache_key_prefix(self):
        """
        Override the cache key prefix to include the user ID to ensure
        each user has their own cache.
        """
        user_id = self.request.user.id if self.request.user and self.request.user.is_authenticated else 'anonymous'
        return f"{self.cache_key_prefix}_{user_id}"
    
    def get(self, request, product_id):
        try:
            product = get_object_or_404(Product, id=product_id)
            
            # Check if the user is the provider of the product or a package maker
            is_provider = hasattr(request.user, 'provider_profile') and product.provider == request.user.provider_profile
            is_package_maker = request.user.role == 'package_maker' if hasattr(request.user, 'role') else False
            
            if not product.isActive and not is_provider:
                return Response({
                    'status': 'error',
                    'message': 'Product not found or inactive',
                    'code': ErrorCodes.NOT_FOUND,
                }, status=status.HTTP_404_NOT_FOUND)
            
            if not (is_provider or is_package_maker):
                raise PermissionDenied("You don't have permission to view this product.")
                
            serializer = ProductSerializer(product)
            return Response({
                'status': 'success',
                'message': 'Product details retrieved successfully',
                'data': serializer.data
            })
        except Product.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Product not found',
                'code': ErrorCodes.NOT_FOUND,
            }, status=status.HTTP_404_NOT_FOUND)
        except PermissionDenied as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'code': ErrorCodes.PERMISSION_DENIED,
            }, status=status.HTTP_403_FORBIDDEN)
        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e),
                'code': ErrorCodes.INTERNAL_ERROR,
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def put(self, request, product_id):
        try:
            product = get_object_or_404(Product, id=product_id)
        except Http404:
            return Response({
                'status': 'error',
                'message': 'Product not found',
                'code': 'RES_001',
                'errors': None
            }, status=status.HTTP_404_NOT_FOUND)

        if request.user != product.provider.user:
            return Response({
                'status': 'error',
                'message': 'You do not have permission to access this product',
                'code': 'PERM_001',
                'errors': None
            }, status=status.HTTP_403_FORBIDDEN)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Product updated successfully."
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, product_id):
        try:
            # Fetch the product by ID and ensure it belongs to the authenticated provider
            user = request.user
            product = Product.objects.filter(id=product_id).first()

            if not product:
                return Response(
                    {
                        "status": "error",
                        "message": "Product not found.",
                        "code": ErrorCodes.NOT_FOUND,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            # check if permitted
            if product.provider != user.provider_profile:
                return Response(
                    {
                        "status": "error",
                        "message": "You do not have permission to access this product",
                        "code": ErrorCodes.PERMISSION_DENIED,
                    },
                    status=status.HTTP_403_FORBIDDEN,
                )

            # Delete the product
            product.delete()
            return Response(
                {
                    "status": "success",
                    "message": "Product deleted successfully"
                },
                status=status.HTTP_200_OK,
            )

        except Exception as e:
            if isinstance(e, (ValidationError, PermissionError, ResourceNotFoundError)):
                raise e
            raise ValidationError(str(e))

class ProductActivateView(APIView):
    permission_classes = [IsAuthenticated, IsProvider]

    def post(self, request, product_id):
        try:
            product = Product.objects.filter(id=product_id).first()
            if not product:
                return Response(
                    {
                        "status": "error",
                        "message": "Product not found.",
                        "code": ErrorCodes.NOT_FOUND,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )

            if request.user != product.provider.user:
                return Response({
                    'status': 'error',
                    'message': 'You do not have permission to access this product',
                    'code': ErrorCodes.PERMISSION_DENIED,
                    'errors': None
                }, status=status.HTTP_403_FORBIDDEN)

            product.isActive = True
            product.save()
            return Response({
                "status": "success",
                "message": "Product activated successfully"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            if isinstance(e, (ValidationError, PermissionError, ResourceNotFoundError)):
                raise e
            raise ValidationError(str(e))

class ProductDeactivateView(APIView):
    permission_classes = [IsAuthenticated, IsProvider]

    def post(self, request, product_id):
        try:
            product = Product.objects.filter(id=product_id).first()
            if not product:
                return Response(
                    {
                        "status": "error",
                        "message": "Product not found.",
                        "code": ErrorCodes.NOT_FOUND,
                    },
                    status=status.HTTP_404_NOT_FOUND,
                )


            if request.user != product.provider.user:
                return Response({
                    'status': 'error',
                    'message': 'You do not have permission to access this product',
                    'code': ErrorCodes.PERMISSION_DENIED,
                    'errors': None
                }, status=status.HTTP_403_FORBIDDEN)

            product.isActive = False
            product.save()
            return Response({
                "status": "success",
                "message": "Product deactivated successfully"
            }, status=status.HTTP_200_OK)

        except Exception as e:
            if isinstance(e, (ValidationError, PermissionError, ResourceNotFoundError)):
                raise e
            raise ValidationError(str(e))

class AllProductsListView(MonitoredCacheMixin, ListAPIView):
    permission_classes = [IsAuthenticated, IsPackageMaker]
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'summary', 'description']
    filterset_class = ProductFilter
    pagination_class = CustomPagination
    cache_timeout = 60 * 5  # 5 minutes
    cache_key_prefix = 'all_products_list'
    
    def get_cache_key_prefix(self):
        """
        Override the cache key prefix to include the user ID to ensure
        each user has their own cache.
        """
        user_id = self.request.user.id if self.request.user and self.request.user.is_authenticated else 'anonymous'
        return f"{self.cache_key_prefix}_{user_id}"
    
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)
        
    def get_queryset(self):
        return Product.objects.filter(isActive=True)

class ProductChangeStockView(APIView):
    permission_classes = [IsAuthenticated, IsProvider]

    def patch(self, request):
        try:
            data = request.data
            updates = data.get('updates', [])
            stock_change = data.get('stockChange', None)

            if not updates or stock_change is None:
                return Response({
                    'status': 'error',
                    'message': 'Invalid input data. Both updates and stockChange are required.',
                    'code': ErrorCodes.INVALID_INPUT,
                }, status=status.HTTP_400_BAD_REQUEST)

            product_ids = [update for update in updates]

            # Use SELECT FOR UPDATE to lock rows and prevent race conditions
            with transaction.atomic():
                products = (
                    Product.objects
                    .select_for_update()
                    .filter(id__in=product_ids, provider=request.user.provider_profile)
                )

                if products.count() != len(product_ids):
                    return Response({
                        'status': 'error',
                        'message': 'One or more products not found or you do not have permission to update them.',
                        'code': ErrorCodes.NOT_FOUND,
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Ensure stock does not go negative before updating
                insufficient_stock = [
                    product.id for product in products
                    if product.stock + stock_change < 0
                ]

                if insufficient_stock:
                    return Response({
                        'status': 'error',
                        'message': f'Insufficient stock for products {insufficient_stock}. Stock cannot go negative.',
                        'code': ErrorCodes.INVALID_INPUT,
                    }, status=status.HTTP_400_BAD_REQUEST)

                # Update stock atomically using F expressions
                Product.objects.filter(id__in=product_ids).update(stock=F('stock') + stock_change)

            return Response({
                'status': 'success',
                'message': 'Stock quantities updated successfully.',
            }, status=status.HTTP_200_OK)

        except Exception as e:
            if isinstance(e, (ValidationError, PermissionError)):
                raise e
            raise ValidationError(str(e))

class ProductBulkDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsProvider]

    def delete(self, request):
        try:
            product_ids = request.query_params.get('productIds', '').split(',')

            if not product_ids:
                return Response({
                    'status': 'error',
                    'message': 'Invalid product IDs.',
                    'code': ErrorCodes.INVALID_INPUT,
                }, status=status.HTTP_400_BAD_REQUEST)

            products = Product.objects.filter(id__in=product_ids, provider=request.user.provider_profile)

            if products.count() != len(product_ids):
                return Response({
                    'status': 'error',
                    'message': 'One or more products not found or you do not have permission to delete them.',
                    'code': ErrorCodes.NOT_FOUND,
                }, status=status.HTTP_404_NOT_FOUND)

            # Delete the products
            products.delete()

            return Response({
                'status': 'success',
                'message': 'Products deleted successfully.',
            }, status=status.HTTP_200_OK)

        except Exception as e:
            if isinstance(e, (ValidationError, PermissionError)):
                raise e
            raise ValidationError(str(e))
