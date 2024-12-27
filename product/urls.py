from django.urls import path
from .views import ProductCreateView

urlpatterns = [
    path('product/', ProductCreateView.as_view(), name='product-create'),
] 