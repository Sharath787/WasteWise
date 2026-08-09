from django.db import models

from django.contrib.auth.models import AbstractUser, BaseUserManager


class UserManager(BaseUserManager):
    def create_user(self, phone, email, full_name, password=None):
        if not phone:
            raise ValueError('Phone number is required')
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

    phone = models.CharField(max_length=15, unique=True)
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)

    USERNAME_FIELD = 'phone'
    objects = UserManager()
    REQUIRED_FIELDS = ['email', 'full_name']

    def __str__(self):
        return f"{self.full_name} ({self.phone})"


class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='customer_profile')
    profile_picture = models.ImageField(upload_to='customer/profile_pictures/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name} ({self.user.phone})"


class AgentProfile(models.Model):
    STATUS = (
        ('pending', 'Pending'),
        ('verified', 'Verified'),
        ('rejected', 'Rejected'),
        ('suspended', 'Suspended'),
    )
    VEHICLE_TYPES = (
        ('bike', 'Bike'),
        ('truck', 'Truck'),
        ('ape', 'Ape'),
    )

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    profile_picture = models.ImageField(upload_to='agent/profile_pictures/', blank=True, null=True)
    license_number = models.CharField(max_length=50, unique=True)
    date_of_birth = models.DateField(blank=True, null=True)
    vehicle_type = models.CharField(max_length=50, choices=VEHICLE_TYPES, blank=True, null=True)
    vehicle_registration_number = models.CharField(max_length=50, blank=True, null=True)
    verification_status = models.CharField(max_length=20, choices=STATUS, default='pending')
    cur_latitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    cur_longitude = models.DecimalField(max_digits=9, decimal_places=6, blank=True, null=True)
    is_available = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.full_name} - {self.vehicle_type} ({self.verification_status})"


