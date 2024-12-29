from django.urls import path
from .views import ProductCreateView, ProductListView, ProductGetView

urlpatterns = [
	path('product/', ProductCreateView.as_view(), name='product-create'),
	path('products/', ProductListView.as_view(), name='product-list'),
	path('product/<int:product_id>/', ProductGetView.as_view(), name='product-get'),
]
