import uuid

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save
from django.dispatch import receiver
from django.utils import timezone


class LoginLogs(models.Model):
    name = models.CharField(max_length=50)
    email = models.EmailField(unique=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Doctor(models.Model):
    class GenderChoices(models.TextChoices):
        MALE = "male", "Male"
        FEMALE = "female", "Female"

    class MaritalStatusChoices(models.TextChoices):
        MARRIED = "married", "Married"
        UNMARRIED = "unmarried", "Unmarried"

    class DesignationChoices(models.TextChoices):
        DOCTOR = "doctor", "Doctor"
        HOD = "hod", "Head of the Department"

    doctor_id = models.UUIDField(
        default=uuid.uuid4, primary_key=True, unique=True, editable=False
    )
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=40, choices=GenderChoices.choices)
    create_id = models.CharField(max_length=100, unique=True)
    email = models.EmailField(unique=True)
    mobile_number = models.CharField(max_length=15, unique=True)
    marital_status = models.CharField(
        max_length=40,
        choices=MaritalStatusChoices.choices,
        null=True,
        blank=True,
    )
    qualification = models.CharField(
        max_length=40,
        null=True,
        blank=True,
    )
    designation = models.CharField(
        max_length=40,
        choices=DesignationChoices.choices,
        null=True,
        blank=True,
    )
    blood_group = models.CharField(max_length=10)
    address = models.TextField(
        null=True,
        blank=True,
    )
    country = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    state = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    city = models.CharField(
        max_length=100,
        null=True,
        blank=True,
    )
    postal_code = models.CharField(max_length=40, null=True, blank=True)
    update_profile = models.ImageField(upload_to="doctor_images/", blank=True)
    bio = models.TextField(null=True, blank=True)
    user_name = models.CharField(max_length=250, null=True, blank=True)
    password = models.CharField(max_length=250, null=True, blank=True)
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="doctors"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.designation}"


class DoctorAvailability(models.Model):

    class DaysOfWeek(models.TextChoices):
        MONDAY = "monday", "Monday"
        TUESDAY = "tuesday", "Tuesday"
        WEDNESDAY = "wednesday", "Wednesday"
        THURSDAY = "thursday", "Thursday"
        FRIDAY = "friday", "Friday"
        SATURDAY = "saturday", "Saturday"
        SUNDAY = "sunday", "Sunday"

    doctor = models.ForeignKey(
        Doctor,
        on_delete=models.CASCADE,
        related_name="availabilities",
        null=True,
        blank=True,
    )
    day_of_week = models.CharField(
        max_length=10, choices=DaysOfWeek.choices, null=True, blank=True
    )
    start_time = models.TimeField(null=True, blank=True)
    end_time = models.TimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(null=True, blank=True, default=None)

    def __str__(self):

        return f"{self.doctor.first_name} - {self.day_of_week} ({self.start_time} - {self.end_time})"


@receiver(pre_save, sender=Doctor)
@receiver(pre_save, sender=DoctorAvailability)
def update_timestamp(sender, instance, **kwargs):

    if instance.pk:
        try:
            existing = sender.objects.get(pk=instance.pk)
            if any(
                getattr(existing, field.name) != getattr(instance, field.name)
                for field in sender._meta.fields
                if field.name not in ["created_at", "updated_at"]
            ):
                instance.updated_at = timezone.now()
        except sender.DoesNotExist:
            pass
    else:
        instance.updated_at = None
