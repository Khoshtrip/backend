from django.urls import path
from .views import ProductCreateView, ProductListView, ProductDetailsView, ImageUploadView, ImageDeleteView, \
    ImageDownloadView, ProductActivateView, ProductDeactivateView

urlpatterns = [
    path('product/', ProductCreateView.as_view(), name='product-create'),
    path('product/<int:product_id>/', ProductDetailsView.as_view(), name='product-get'),
    path('product/<int:product_id>/activate', ProductActivateView.as_view(), name='product-activate'),
    path('product/<int:product_id>/deactivate', ProductDeactivateView.as_view(), name='product-deactivate'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('image/upload/', ImageUploadView.as_view(), name='image-upload'),
    path('image/<int:imageId>/', ImageDeleteView.as_view(), name='image-delete'),
    path('image/<int:imageId>/download/', ImageDownloadView.as_view(), name='image-download'),
]
