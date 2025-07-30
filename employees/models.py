from django.db import models
from accounts.models import User

# Create your models here.
class Department(models.Model):
    DEPARTMENT_CHOICES = [
        ('communication', 'Communication'),
        ('creatives', 'Creatives'),
        ('tech_department', 'Tech Department'),
        ('community_experience', 'Community Experience'),
        ('youth_engagement', 'Youth Engagement'),
        ('heritage', 'Heritage'),
        ('admin', 'Admin'),
        ('finance', 'Finance'),
        ('entrepreneurship', 'Entrepreneurship'),
    ]
    
    name = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES, unique=True)
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_department')
                                                  
    def __str__(self):
        return self.get_name_display()
    
    def calculate_performance_score(self):
        """Calculate department performance based on timely report submissions"""
        from core.models import MonthlyReport
        from django.utils import timezone
        from datetime import datetime, timedelta
        
        # Get reports from last 30 days
        thirty_days_ago = timezone.now().date() - timedelta(days=30)
        department_reports = MonthlyReport.objects.filter(
            employee__department=self,
            submitted_at__gte=thirty_days_ago
        )
        
        if not department_reports.exists():
            return 0
        
        # Calculate timely submissions (submitted within first 5 days of month)
        timely_reports = 0
        total_reports = department_reports.count()
        
        for report in department_reports:
            # Consider reports submitted within first 5 days as "on time"
            if report.submitted_at.day <= 5:
                timely_reports += 1
        
        return round((timely_reports / total_reports) * 100, 1) if total_reports > 0 else 0
