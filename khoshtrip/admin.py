from django.contrib import admin
from .models import CustomerUser, ProviderUser

admin.site.register(CustomerUser)
admin.site.register(ProviderUser)
