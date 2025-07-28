
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.crypto import get_random_string

# Create your models here
class User(AbstractUser):
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('hod', 'Head of Department'),
        ('hr', 'HR'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    department = models.ForeignKey('employees.Department', on_delete=models.SET_NULL, null=True, blank=True)
    email_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.username
        
    def generate_verification_token(self):
        """Generate a random token for email verification"""
        token = get_random_string(64)
        self.verification_token = token
        self.save(update_fields=['verification_token'])
        return token