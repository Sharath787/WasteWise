from django.core.exceptions import ValidationError
from django.db import models

from base.models import BaseModel
from users.models import CustomerAddress, User
from yards.models import WasteType, Yard


# Create your models here.
class Booking(BaseModel):
    # Moved to TextChoices for better readability and maintainability
    # Status and PickupType are now defined as inner classes using TextChoices
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        AGENT_ASSIGNED = "agent_assigned", "Agent Assigned"
        AGENT_EN_ROUTE = "agent_en_route", "Agent En Route"
        AGENT_ARRIVED = "agent_arrived", "Agent Arrived"
        PICKED_UP = "picked_up", "Picked Up"
        AT_YARD = "at_yard", "At Yard"
        DUMPED = "dumped", "Dumped"
        COMPLETED = "completed", "Completed"
        CANCELLED = "cancelled", "Cancelled"

    class PickupType(models.TextChoices):
        SCHEDULED = "scheduled", "Scheduled"
        ON_DEMAND = "on_demand", "On Demand"

    # Relationships with other models
    customer = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="bookings"
    )
    agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="agent_bookings",
    )
    yard = models.ForeignKey(
        Yard, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings"
    )
    waste_type = models.ForeignKey(
        WasteType, on_delete=models.PROTECT, related_name="bookings"
    )
    pickup_address = models.ForeignKey(
        CustomerAddress,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="bookings",
    )

    # Location
    pickup_latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    pickup_longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )

    # Status and Pickup Type
    status = models.CharField(
        max_length=20, choices=Status.choices, default=Status.PENDING
    )
    pickup_type = models.CharField(
        max_length=20, choices=PickupType.choices, default=PickupType.ON_DEMAND
    )
    scheduled_pickup_time = models.DateTimeField(blank=True, null=True)

    # details about the booking
    estimated_weight_kg = models.FloatField(blank=True, null=True)
    actual_weight_kg = models.FloatField(blank=True, null=True)
    cost = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    notes = models.TextField(blank=True, null=True)

    def clean(self):
        has_saved_address = self.pickup_address is not None
        has_coordinates = (
            self.pickup_latitude is not None and self.pickup_longitude is not None
        )
        if not (has_saved_address or has_coordinates):
            raise ValidationError(
                "Either a saved address or pickup coordinates must be provided."
            )

        if (
            self.pickup_type == self.PickupType.SCHEDULED
            and not self.scheduled_pickup_time
        ):
            raise ValidationError(
                "Scheduled pickup time must be provided for scheduled pickups."
            )

    def __str__(self):
        return f"Booking {self.id} - {self.customer.full_name} - {self.status}"
