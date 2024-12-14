from django.contrib import admin
from .models import CustomerUser, ProviderUser, VerificationCode

admin.site.register(CustomerUser)
admin.site.register(ProviderUser)
@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('mobile_number', 'code', 'expiration')
    search_fields = ('mobile_number',)
