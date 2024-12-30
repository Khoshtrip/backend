from django.shortcuts import get_object_or_404
from rest_framework.exceptions import PermissionDenied
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import ProductSerializer
from rest_framework.permissions import IsAuthenticated
from authorization.permissions import IsProvider
from utils.exceptions import ValidationError, PermissionError
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
                    'code': 'VAL_003',
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
            if request.user != product.provider.user:
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
        except Product.DoesNotExist:
            return Response({
                'status': 'error',
                'message': 'Product not found',
                'code': 'RES_001',
                'errors': None
            }, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, product_id):
        product = get_object_or_404(Product, id=product_id)
        if request.user != product.provider.user:
            raise PermissionDenied("You do not have permission to access this product.")
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response({
                "status": "success",
                "message": "Product updated successfully."
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, productId):
        # TODO
        pass
