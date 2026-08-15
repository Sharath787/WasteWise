from django.db import models

from base.models import BaseModel

# Create your models here.


class WasteType(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.name


class Yard(BaseModel):
    name = models.CharField(max_length=100, unique=True)
    contact_number = models.CharField(max_length=15, unique=True)
    address = models.CharField(max_length=255)
    lattitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_active = models.BooleanField(default=True)
    opens_at = models.TimeField()
    closes_at = models.TimeField()
    waste_types = models.ManyToManyField(WasteType, through="YardWasteCapacity")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name


class YardWasteCapacity(BaseModel):
    yard = models.ForeignKey(Yard, on_delete=models.CASCADE)
    waste_type = models.ForeignKey(WasteType, on_delete=models.CASCADE)
    capacity = models.FloatField()  # Capacity in tons or any other unit you prefer
    current_fill_kg = models.FloatField(default=0.0)  # Current fill in kilograms

    class Meta:
        unique_together = ("yard", "waste_type")

    def __str__(self):
        return f"{self.yard.name} - {self.waste_type.name} Capacity: {self.capacity}"
