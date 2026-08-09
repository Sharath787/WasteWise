from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, CustomerProfile, AgentProfile

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('phone',)
    list_display = ('phone', 'email', 'full_name', 'is_active')
    fieldsets = (
        (None, {'fields': ('phone','password')}),
        ('Personal Info', {'fields': ('full_name', 'email')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
    )

    add_fieldsets = (
        (None, {'classes': 'wide', 'fields': ('phone', 'email', 'full_name', 'password1', 'password2')}),
    )


@admin.register(CustomerProfile)
class CustomerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'created_at')


@admin.register(AgentProfile)
class AgentProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'vehicle_type', 'verification_status', 'is_available')
    list_filter = ('verification_status', 'is_available')

