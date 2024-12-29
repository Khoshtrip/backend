from django_filters import rest_framework as filters
from .models import Product

class ProductFilter(filters.FilterSet):
    minPrice = filters.NumberFilter(field_name='price', lookup_expr='gte')
    maxPrice = filters.NumberFilter(field_name='price', lookup_expr='lte')
    stockAvailable = filters.BooleanFilter(method='filter_stock_available')
    
    class Meta:
        model = Product
        fields = ['category', 'isActive']
        
    def filter_stock_available(self, queryset, name, value):
        if value:  # If stockAvailable is True
            return queryset.filter(stock__gt=0)
        return queryset.filter(stock=0) 