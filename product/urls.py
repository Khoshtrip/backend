from django.urls import path
from .views import ProductCreateView, ProductListView, ImageUploadView, ImageDeleteView, ImageDownloadView

urlpatterns = [
    path('product/', ProductCreateView.as_view(), name='product-create'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('image/upload/', ImageUploadView.as_view(), name='image-upload'),
    path('image/<int:imageId>/', ImageDeleteView.as_view(), name='image-delete'),
    path('image/<int:imageId>/download/', ImageDownloadView.as_view(), name='image-download'),
] 