from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('user_id', 'username', 'role', 'name', 'email', 'is_staff', 'id')
    search_fields = ('user_id', 'name', 'email', 'contact_number')
    list_filter = ('role', 'is_staff', 'is_superuser')

    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('name', 'email', 'contact_number', 'profile_picture', 'company_logo')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
        ('Custom Info', {'fields': ('role', 'user_id', 'is_rented', 'rented_event_id')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'password1', 'password2', 'role', 'user_id', 'is_rented', 'rented_event_id'),
        }),
    )
