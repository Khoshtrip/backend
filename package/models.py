from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from product.models import Product, Image

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

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.start_date and self.end_date and self.start_date >= self.end_date:
            raise ValidationError('Start date must be before end date')

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name
