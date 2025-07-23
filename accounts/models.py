
from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here
class User(AbstractUser):
    ROLE_CHOICES = [
        ('employee', 'Employee'),
        ('hod', 'Head of Department'),
        ('hr', 'HR'),
    ]
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='employee')
    department = models.ForeignKey('employees.Department', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.username