import uuid
from time import timezone

from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models

from base.models import BaseModel


class UserManager(BaseUserManager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

    def create_user(self, phone, email, full_name, password=None):
        if not phone:
            raise ValueError("Phone number is required")
        email = self.normalize_email(email)
        user = self.model(phone=phone, email=email, full_name=full_name)
        user.set_unusable_password()
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, email, full_name, password=None):
        email = self.normalize_email(email)
        user = self.model(phone=phone, email=email, full_name=full_name)
        user.set_password(password)
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractUser):
    first_name = None
    last_name = None
    username = None
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)
    is_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(blank=True, null=True)

    USERNAME_FIELD = "phone"
    objects = UserManager()
    all_objects = (
        models.Manager()
    )  # This manager returns all records, including deleted ones
    REQUIRED_FIELDS = ["email", "full_name"]

    def __str__(self):
        return f"{self.full_name} ({self.phone})"

    def soft_delete(self):
        """Soft delete the user by setting is_deleted to True."""
        self.is_deleted = True
        self.deleted_at = timezone.now()
        self.save()


class CustomerProfile(BaseModel):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="customer_profile"
    )
    profile_picture = models.ImageField(
        upload_to="customer/profile_pictures/", blank=True, null=True
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name} ({self.user.phone})"


class AgentProfile(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending", "Pending"
        VERIFIED = "verified", "Verified"
        REJECTED = "rejected", "Rejected"
        SUSPENDED = "suspended", "Suspended"

    class VehicleType(models.TextChoices):
        BIKE = "bike", "Bike"
        TRUCK = "truck", "Truck"
        APE = "ape", "Ape"

    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="agent_profile"
    )
    profile_picture = models.ImageField(
        upload_to="agent/profile_pictures/", blank=True, null=True
    )
    license_number = models.CharField(max_length=50, unique=True)
    date_of_birth = models.DateField(blank=True, null=True)
    vehicle_type = models.CharField(
        max_length=50, choices=VehicleType.choices, blank=True, null=True
    )
    vehicle_registration_number = models.CharField(max_length=50, blank=True, null=True)
    verification_status = models.CharField(
        max_length=20, choices=Status.choices, default="pending"
    )
    cur_latitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    cur_longitude = models.DecimalField(
        max_digits=9, decimal_places=6, blank=True, null=True
    )
    is_available = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return (
            f"{self.user.full_name} - {self.vehicle_type} ({self.verification_status})"
        )


class CustomerAddress(BaseModel):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="addresses")
    label = models.CharField(max_length=100)
    address = models.CharField(max_length=500)
    latitude = models.DecimalField(max_digits=9, decimal_places=6)
    longitude = models.DecimalField(max_digits=9, decimal_places=6)
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.label} - {self.address}"
