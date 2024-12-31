from django.db import models
from django.utils import timezone
from authorization.models import ProviderProfile
from django.db import models


class Image(models.Model):
    id = models.AutoField(primary_key=True)
    file = models.ImageField(upload_to='uploads/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    # uploader = models.ForeignKey(
    #     'auth.User', on_delete=models.CASCADE, related_name='images'
    # )

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('flight', 'Flight Ticket'),
        ('train', 'Train Ticket'),
        ('bus', 'Bus Ticket'),
        ('hotel', 'Hotel'),
        ('tourism', 'Tourism Ticket'),
        ('restaurant', 'Restaurant'),
    ]

    name = models.CharField(max_length=255)
    summary = models.CharField(max_length=500)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    stock = models.IntegerField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    images = models.JSONField(default=list)
    isActive = models.BooleanField(default=True)
    provider = models.ForeignKey(ProviderProfile, on_delete=models.CASCADE, related_name='products')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
