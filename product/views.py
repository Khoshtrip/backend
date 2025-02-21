from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from utils.error_codes import ErrorCodes
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated
from authorization.permissions import IsProvider
from utils.exceptions import ValidationError, PermissionError, ResourceNotFoundError
from rest_framework.generics import ListAPIView
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter
from .models import Product
from .pagination import CustomPagination
from .filters import ProductFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from django.http import FileResponse, Http404
from .models import Image
from rest_framework.permissions import AllowAny
from authorization.permissions import IsPackageMaker

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


class ProductDetailsView(APIView):
    def get(self, request, product_id):
        try:
            product = get_object_or_404(Product, id=product_id)
        except Http404:
            return Response({
                'status': 'error',
                'message': 'Product not found',
                'code': ErrorCodes.NOT_FOUND,
                'errors': None
            }, status=status.HTTP_404_NOT_FOUND)

        if (request.user != product.provider.user) and (request.user.role != 'package_maker'):
            return Response({
                'status': 'error',
                'message': 'You do not have permission to access this product',
                'code': 'PERM_001',
                'errors': None
            }, status=status.HTTP_403_FORBIDDEN)

        serializer = ProductSerializer(product)
        return Response({
            'status': 'success',
            'message': 'Product retrieved successfully',
            'data': serializer.data
        }, status=status.HTTP_200_OK)

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

class AllProductsListView(ListAPIView):
    permission_classes = [IsAuthenticated, IsPackageMaker]
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter]
    search_fields = ['name', 'summary', 'description']
    filterset_class = ProductFilter
    pagination_class = CustomPagination

    def get_queryset(self):
        queryset = Product.objects.filter(isActive=True)
        product_type = self.request.query_params.get('type', None)
        
        if product_type:
            # Split the type parameter in case multiple types are provided
            product_types = product_type.split(',')
            # Filter for the specified product types
            queryset = queryset.filter(category__in=product_types)
        
        return queryset

    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'status': 'success',
            'message': 'Products retrieved successfully',
            'data': serializer.data
        })