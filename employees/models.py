from django.db import models
from accounts.models import User

# Create your models here.
class Department(models.Model):
    name = models.CharField(max_length=100)
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_department')
                                                  
    def __str__(self):
        return self.name
