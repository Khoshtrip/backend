from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator, URLValidator
from django.utils.timezone import now


class BaseUser(AbstractUser):
	birth_date = models.DateField(null=True, blank=True)
	mobile_number = models.CharField(max_length=15, blank=True)
	id_number = models.CharField(
		max_length=10,
		validators=[RegexValidator(r'^\d{10}$', 'ID number must be exactly 10 digits.')],
		unique=True
	)


class CustomerUser(BaseUser):
	def __str__(self):
		return f"{self.username} ({self.email})"


class ProviderUser(BaseUser):
	business_name = models.CharField(max_length=255)
	business_address = models.TextField()
	website_url = models.URLField(validators=[URLValidator()], blank=True, null=True)

	def __str__(self):
		return f"{self.username} ({self.business_name})"


class VerificationCode(models.Model):
	mobile_number = models.CharField(max_length=15, unique=True)  # Mobile number (unique)
	code = models.CharField(max_length=6)  # 6-digit code stored as a string
	expiration = models.DateTimeField()  # Expiration timestamp

	# TODO: Maybe it is the best practice to periodically delete expired codes.

	def is_expired(self):
		return now() > self.expiration

	def __str__(self):
		return f"{self.mobile_number} - {self.code} (Expires: {self.expiration})"
