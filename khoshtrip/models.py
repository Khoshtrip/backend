from django.core.validators import RegexValidator
from django.db import models


class User(models.Model):
    username = models.CharField(max_length=150, unique=True)
    password = models.CharField(max_length=128)  # Using Django auth system is recommended for hashed password
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    birth_date = models.DateField()
    mobile_number = models.CharField(
        max_length=15,
        validators=[
            RegexValidator(
                regex=r'^\+?\d{9,15}$',
                message="Mobile number is not in the correct format"
            )
        ]
    )
    id_number = models.CharField(
        max_length=10,
        validators=[
            RegexValidator(
                regex=r'^\d{10}$',
                message="ID number must be exactly 10 digits."
            )
        ]
    )
    email_address = models.EmailField(unique=True)

    def __str__(self):
        return self.username
