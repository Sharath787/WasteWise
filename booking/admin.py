from django.contrib import admin

from .models import Booking


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "customer",
        "agent",
        "waste_type",
        "status",
        "pickup_type",
        "created_at",
    )
    list_filter = ("status", "pickup_type", "waste_type")
    search_fields = ("customer__phone", "customer__full_name", "agent__phone")
    readonly_fields = ("id", "created_at", "updated_at")
