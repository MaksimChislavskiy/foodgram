from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User


class CustomUserAdmin(BaseUserAdmin):
    list_display = ('username',
                    'id',
                    'email',
                    'first_name',
                    'last_name',
                    'avatar')
    list_filter = ('email', 'first_name', 'is_staff')
    search_fields = ('email', 'first_name', 'last_name')


admin.site.register(User, CustomUserAdmin)
