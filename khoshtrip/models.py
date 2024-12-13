from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, URLValidator


class CustomerUser(AbstractUser):
    birth_date = models.DateField(null=True, blank=True)
    mobile_number = models.CharField(max_length=15, blank=True)
    id_number = models.CharField(
        max_length=10,
        validators=[RegexValidator(r'^\d{10}$', 'ID number must be exactly 10 digits.')],
        unique=True
    )
    email_address = models.EmailField(unique=True)

    def __str__(self):
        return f"{self.username} ({self.email_address})"


class ProviderUser(CustomerUser):
    business_name = models.CharField(max_length=255)
    business_address = models.TextField()
    business_contact = models.CharField(max_length=15)
    website_url = models.URLField(validators=[URLValidator()], blank=True, null=True)

    def __str__(self):
        return f"{self.business_name} ({self.username})"
