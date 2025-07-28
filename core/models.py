from django.db import models
from accounts.models import User

# Create your models here.
class EmployeeProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def __str__(self):
        return f"{self.user.username}'s Profile"

class LeaveRequest(models.Model):
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('hod_approved', 'HOD Approved'),
        ('hr_approved', 'HR Approved'),
        ('rejected', 'Rejected'),
    ]
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    hod_approval = models.BooleanField(default=False)
    hr_approval = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} - {self.start_date} to {self.end_date}"

class Attendance(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    check_in_time = models.DateTimeField()
    note = models.TextField(blank=True)

    def __str__(self):
        return f"{self.employee.username} - {self.date}"

class MonthlyReport(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    month = models.DateField()
    file = models.FileField(upload_to='reports/', null=True, blank=True)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} - {self.month.strftime('%B %Y')}"

class Appraisal(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appraisals')
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluations')
    score = models.IntegerField()
    comments = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} - {self.date}"
