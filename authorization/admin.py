from django.contrib import admin
from .models import BaseUser, VerificationCode, TokenBlacklist, ProviderProfile

@admin.register(BaseUser)
class BaseUserAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'first_name', 'last_name', 'role', 'is_active', 'is_staff', 'date_joined')
    search_fields = ('phone_number', 'email', 'first_name', 'last_name')
    list_filter = ('is_active', 'is_staff', 'role')


@admin.register(ProviderProfile)
class ProviderProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'business_name', 'business_contact', 'website_url')


@admin.register(VerificationCode)
class VerificationCodeAdmin(admin.ModelAdmin):
    list_display = ('phone_number', 'code', 'created_at', 'is_used')
    search_fields = ('phone_number',)
    list_filter = ('is_used',)


@admin.register(TokenBlacklist)
class TokenBlacklistAdmin(admin.ModelAdmin):
    list_display = ('token', 'blacklisted_at')
