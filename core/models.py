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
    STATUS_CHOICES = [
        ('on_time', 'On Time'),
        ('late', 'Late'),
        ('absent', 'Absent'),
    ]
    
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    check_in_time = models.DateTimeField()
    note = models.TextField(blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='on_time')

    class Meta:
        unique_together = ['employee', 'date']  # Prevent multiple check-ins per day
        ordering = ['-date', '-check_in_time']

    def __str__(self):
        return f"{self.employee.username} - {self.date} ({self.get_status_display()})"
    
    def save(self, *args, **kwargs):
        """Calculate status based on check-in time (9 AM Nairobi time)"""
        if self.check_in_time:
            from django.utils import timezone
            import pytz
            
            # Convert check-in time to Nairobi timezone
            nairobi_tz = pytz.timezone('Africa/Nairobi')
            if timezone.is_naive(self.check_in_time):
                check_in_nairobi = nairobi_tz.localize(self.check_in_time)
            else:
                check_in_nairobi = self.check_in_time.astimezone(nairobi_tz)
            
            # Create 9 AM deadline for the same date in Nairobi timezone
            deadline = nairobi_tz.localize(
                timezone.datetime.combine(self.date, timezone.datetime.min.time().replace(hour=9))
            )
            
            # Determine status
            if check_in_nairobi <= deadline:
                self.status = 'on_time'
            else:
                self.status = 'late'
        
        super().save(*args, **kwargs)

class MonthlyReport(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE)
    report_date = models.DateField()  # Date the report is for
    file = models.FileField(upload_to='reports/%Y/%m/', null=False, blank=False)  # Required file upload
    description = models.TextField(blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)  # When it was submitted
    
    class Meta:
        unique_together = ['employee', 'report_date']  # Prevent duplicate reports for same month
        ordering = ['-submitted_at']

    def __str__(self):
        return f"{self.employee.username} - {self.report_date.strftime('%B %Y')} (Submitted: {self.submitted_at.strftime('%Y-%m-%d %H:%M')})"
    
    def is_submitted_on_time(self):
        """Check if report was submitted within the first 5 days of the following month"""
        from datetime import datetime, timedelta
        from django.utils import timezone
        import calendar
        
        # Get the last day of the report month
        last_day = calendar.monthrange(self.report_date.year, self.report_date.month)[1]
        
        # Create timezone-aware deadline
        deadline = timezone.make_aware(datetime(
            self.report_date.year if self.report_date.month < 12 else self.report_date.year + 1,
            self.report_date.month + 1 if self.report_date.month < 12 else 1,
            5,  # 5th day of next month
            23, 59, 59  # End of day
        ))
        
        # Ensure submitted_at is timezone-aware (it should be since it's auto_now_add=True)
        submitted_time = self.submitted_at
        if timezone.is_naive(submitted_time):
            submitted_time = timezone.make_aware(submitted_time)
            
        return submitted_time <= deadline

class Appraisal(models.Model):
    employee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='appraisals')
    evaluator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='evaluations')
    score = models.IntegerField()
    comments = models.TextField()
    date = models.DateField(auto_now_add=True)

    def __str__(self):
        return f"{self.employee.username} - {self.date}"
