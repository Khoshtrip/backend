from django.urls import path
from .views import ProductCreateView, ProductListView, ProductDetailsView, ImageUploadView, ImageDeleteView, \
    ImageDownloadView, ProductActivateView, ProductDeactivateView, ProductChangeStockView, ProductBulkDeleteView, AllProductsListView

urlpatterns = [
    path('product/', ProductCreateView.as_view(), name='product-create'),
    path('product/<int:product_id>/', ProductDetailsView.as_view(), name='product-get'),
    path('product/<int:product_id>/activate', ProductActivateView.as_view(), name='product-activate'),
    path('product/<int:product_id>/deactivate', ProductDeactivateView.as_view(), name='product-deactivate'),
    path('product/changeProductsAmountBy', ProductChangeStockView.as_view(), name='change-products-stock'),
    path('product/delete', ProductBulkDeleteView.as_view(), name='bulk-delete-products'),
    path('products/', ProductListView.as_view(), name='product-list'),
    path('products/all/', AllProductsListView.as_view(), name='all-products-list'),
    path('image/upload/', ImageUploadView.as_view(), name='image-upload'),
    path('image/<int:imageId>/', ImageDeleteView.as_view(), name='image-delete'),
    path('image/<int:imageId>/download/', ImageDownloadView.as_view(), name='image-download'),
]
