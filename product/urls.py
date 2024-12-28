from django.urls import path
from .views import ProductCreateView, ProductListView

urlpatterns = [
    path('product/', ProductCreateView.as_view(), name='product-create'),
    path('products/', ProductListView.as_view(), name='product-list'),
] 