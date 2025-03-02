from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone

from authorization.models import BaseUser
from product.models import Product, Image
from django.contrib.auth import get_user_model
from django.db.models import Q

User = get_user_model()

class TripPackage(models.Model):
    name = models.CharField(max_length=100)
    photos = models.JSONField(default=list)  # List of image IDs
    flight = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='flight_packages', limit_choices_to={'category': 'flight'})
    hotel = models.ForeignKey(Product, on_delete=models.PROTECT, related_name='hotel_packages', limit_choices_to={'category': 'hotel'})
    activities = models.ManyToManyField(Product, blank=True, related_name='activity_packages', limit_choices_to={'category__in': ['tourism', 'restaurant']})
    price = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(0.01)])
    start_date = models.DateField()
    end_date = models.DateField()
    available_units = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    published = models.BooleanField(default=False)
    description = models.TextField(max_length=500, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError('Start date must be before end date')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    @classmethod
    def filter_packages(cls, **kwargs):
        queryset = cls.objects.select_related('flight', 'hotel').prefetch_related('activities')
        
        # Search by name
        if search := kwargs.get('search'):
            queryset = queryset.filter(name__icontains=search)
        
        # Filter by price range
        if price_min := kwargs.get('price_min'):
            queryset = queryset.filter(price__gte=price_min)
        if price_max := kwargs.get('price_max'):
            queryset = queryset.filter(price__lte=price_max)
        
        # Filter by date range
        if date_start := kwargs.get('date_start'):
            queryset = queryset.filter(start_date__gte=date_start)
        if date_end := kwargs.get('date_end'):
            queryset = queryset.filter(end_date__lte=date_end)

        # Filter by hotel name
        if hotel_name := kwargs.get('hotel_name'):
            queryset = queryset.filter(hotel__name__icontains=hotel_name)

        # Filter by airline name
        if flight_airline := kwargs.get('flight_airline'):
            queryset = queryset.filter(flight__name__icontains=flight_airline)

        # Filter by published status
        if 'published' in kwargs:
            queryset = queryset.filter(published=kwargs['published'])

        # Sort by price or date
        if sort_by := kwargs.get('sort_by'):
            if sort_by == 'price':
                queryset = queryset.order_by('price')
            elif sort_by == 'date':
                queryset = queryset.order_by('start_date')

        return queryset

class Transaction(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]

    transaction_id = models.CharField(max_length=100, unique=True)  # Unique transaction ID
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='transactions')  # Link to the User model
    package = models.ForeignKey('TripPackage', on_delete=models.CASCADE, related_name='transactions')
    created_at = models.DateTimeField(default=timezone.now)  # Timestamp of the transaction creation
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')  # Transaction status
    quantity = models.PositiveIntegerField(default=1)  # Number of packages to buy

    # Fields for completed transactions
    purchase_date = models.DateTimeField(null=True, blank=True)  # Timestamp of the purchase confirmation
    card_number = models.CharField(max_length=16, null=True, blank=True)  # Last 4 digits of the card

    def __str__(self):
        return f"Transaction {self.transaction_id} for Package {self.package.name} (Status: {self.status})"

class PurchaseHistory(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='purchase_history')
    package = models.ForeignKey('TripPackage', on_delete=models.CASCADE, related_name='purchase_history')
    transaction = models.OneToOneField('Transaction', on_delete=models.CASCADE, related_name='purchase_history')
    purchase_date = models.DateTimeField(default=timezone.now)
    quantity = models.PositiveIntegerField(default=1)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Purchase by {self.user.phone_number} for {self.package.name} on {self.purchase_date}"
