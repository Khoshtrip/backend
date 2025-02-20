from django.contrib import admin
from .models import TripPackage

@admin.register(TripPackage)
class TripPackageAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'start_date', 'end_date', 'available_units', 'published')
    list_filter = ('published', 'start_date', 'end_date')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('activities',)
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'description', 'price', 'available_units', 'published')
        }),
        ('Dates', {
            'fields': ('start_date', 'end_date')
        }),
        ('Media', {
            'fields': ('photos',)
        }),
        ('Products', {
            'fields': ('flight', 'hotel', 'activities')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
