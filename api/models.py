from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator, FileExtensionValidator
from datetime import timedelta
from django.core.exceptions import ValidationError
import re
# Create your models here.


class Subscriber(models.Model):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    # is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email


class Blog(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField(blank=True, null=True)
    category = models.CharField(max_length=50, blank=True, null=True)

    author = models.CharField(max_length=50)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to="blogimages", blank=True)

    date_created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    read_time = models.DurationField(default=timedelta(minutes=8))

    def __str__(self):
        return self.title


class ContactMessage(models.Model):

    STATUS_CHOICES = (
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived')
    )

    phone_regex = RegexValidator(
        regex=r'^\+977\d{10}$',
        message="Phone number must start with +977 and contain exactly 10 digits after it."
    )

    name = models.CharField(max_length=50)
    email = models.EmailField(blank=False, null=False)
    phone = models.CharField(
        max_length=14,
        validators=[phone_regex]
    )
    address = models.CharField(max_length=50)
    subject = models.CharField(max_length=50)
    message = models.TextField()
    status = models.CharField(
        max_length=10,
        default='new',
        choices=STATUS_CHOICES,
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.email} - {self.subject or 'No Subject'}"


class Internship(models.Model):
    title = models.CharField(max_length=50)
    description = models.TextField()
    image = models.ImageField(
        upload_to="internimages",
        blank=True,
        null=True
    )
    total_seats = models.IntegerField()
    is_open = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    @property
    def available_seats(self):
        # If i had applications, i would subtract them here
        # For now,let's just return total_seats
        return self.total_seats

def validate_file_size(value):
        filesize  = value.size
        if filesize > 5 * 1024 *1024:
            raise ValidationError("File too large. File size cannot exceed 5 MiB.")
        return value

class InternshipApplication(models.Model):
    GENDER_CHOICES = (
        ('male', 'Male'),
        ('female', 'Female'),
        ('other', 'Other')
    )

    contact_regex = RegexValidator(
        regex=r'^\+977\s?\d{10}$',
        message="Phone number must start with +977 and contain exactly 10 digits(e.g., +977 98XXXXXXXX) after it."
    )

    full_name = models.CharField(max_length=100)
    duration = models.CharField(max_length=20)
    college_name = models.CharField(max_length=200)
    contact_number = models.CharField(
        max_length=15,
        validators=[contact_regex]
    )
    email = models.EmailField()
    dob = models.DateField()
    gender = models.CharField(
        max_length=10,
        choices=GENDER_CHOICES,
        default='male'
    )
    address = models.CharField(max_length=255)
    internship_title = models.CharField(max_length=100)
    
    cv_file = models.FileField(
        upload_to='cvs/',
        validators=[
            FileExtensionValidator(allowed_extensions=['pdf', 'doc', 'docx']),
            validate_file_size
        ]
    )

    applied_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.full_name} - {self.internship_title}"

