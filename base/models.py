from django.db import models
import uuid
from django.utils import timezone


class ActiveManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_deleted=False)

class BaseModel(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_deleted = models.BooleanField(default=False)

    objects = ActiveManager()  # Default manager returns only active records
    all_objects = models.Manager()  # This manager returns all records, including deleted ones

    class Meta:
        abstract = True  # This model will not be used to create any database table

    def soft_delete(self):
        """Soft delete the record by setting is_deleted to True."""
        self.is_deleted = True
        self.save()

# Create your models here.
