from django.contrib import admin
from .models import Product

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'provider', 'price', 'stock', 'category', 'isActive', 'created_at', 'updated_at')
    list_filter = ('category', 'isActive', 'provider')
    search_fields = ('name', 'summary', 'description')
    readonly_fields = ('created_at', 'updated_at')
    list_per_page = 25
