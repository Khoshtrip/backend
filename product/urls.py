from django.urls import path
from .views import ProductCreateView, ProductListView, ProductDetailsView

urlpatterns = [
    path('product/', ProductCreateView.as_view(), name='product-create'),
    path('product/<int:product_id>/', ProductDetailsView.as_view(), name='product-get'),
    path('products/', ProductListView.as_view(), name='product-list'),
]