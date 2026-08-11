from django.contrib import admin

from .models import WasteType, Yard, YardWasteCapacity


@admin.register(WasteType)
class WasteTypeAdmin(admin.ModelAdmin):
    list_display = ("name", "description")


class YardWasteCapacityInline(admin.TabularInline):
    model = YardWasteCapacity
    extra = 1


@admin.register(Yard)
class YardAdmin(admin.ModelAdmin):
    list_display = ("name", "address", "contact_number", "is_active")
    list_filter = ("is_active",)
    inlines = [YardWasteCapacityInline]
