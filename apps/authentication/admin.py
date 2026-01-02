from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from django.utils.html import format_html

from .models import UserProfile



@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'phone_number',
        'role',
        'is_email_verified',
        'created_at',
    )

    list_filter = ('role', 'is_email_verified')
    search_fields = ('user__username', 'user__email')
    ordering = ('-created_at',)

