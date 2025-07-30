from django import forms
from django.core.exceptions import ValidationError
from accounts.models import User
from core.models import LeaveRequest, MonthlyReport, Appraisal, Attendance

class LeaveRequestForm(forms.ModelForm):
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'}),
            'end_date': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent'}),
            'reason': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent', 'rows': '4'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get('start_date')
        end_date = cleaned_data.get('end_date')
        
        if start_date and end_date and start_date > end_date:
            raise ValidationError("End date cannot be before start date.")
        
        return cleaned_data

class MonthlyReportForm(forms.ModelForm):
    report_month = forms.CharField(
        widget=forms.Select(choices=[]),
        label="Report Month/Year",
        help_text="Select the month and year this report covers"
    )
    
    class Meta:
        model = MonthlyReport
        fields = ['description', 'file']
        widgets = {
            'description': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent', 
                'rows': '6',
                'placeholder': 'Describe your monthly report and key accomplishments...'
            }),
            'file': forms.FileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent', 
                'accept': '.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt'
            }),
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Generate month choices for the current year and next year
        from datetime import datetime, timedelta
        import calendar
        
        current_date = datetime.now()
        choices = []
        
        # Get existing reports for this user if available
        existing_reports = set()
        if hasattr(self, 'user') and self.user:
            existing_reports = set(
                MonthlyReport.objects.filter(employee=self.user)
                .values_list('report_date', flat=True)
            )
        
        # Add months from 6 months ago to 12 months in the future
        for i in range(-6, 13):
            # More accurate month calculation
            year = current_date.year
            month = current_date.month + i
            
            # Handle year overflow/underflow
            while month > 12:
                month -= 12
                year += 1
            while month < 1:
                month += 12
                year -= 1
                
            month_date = datetime(year, month, 1)
            month_value = month_date.strftime('%Y-%m-01')
            month_label = month_date.strftime('%B %Y')
            
            # Check if this month already has a report
            report_date = month_date.date()
            if report_date in existing_reports:
                month_label += " (Already Submitted)"
            
            choices.append((month_value, month_label))
        
        self.fields['report_month'].widget.choices = choices
        self.fields['file'].required = True
        self.fields['file'].help_text = "Accepted formats: PDF, Word, Excel, PowerPoint, Text files (Max size: 10MB)"
        
    def save(self, commit=True):
        instance = super().save(commit=False)
        from datetime import datetime
        # Convert the selected month string to a date
        instance.report_date = datetime.strptime(self.cleaned_data['report_month'], '%Y-%m-%d').date()
        if commit:
            instance.save()
        return instance
    
    def clean_report_month(self):
        report_month = self.cleaned_data['report_month']
        from datetime import datetime
        
        # Convert to date for checking
        report_date = datetime.strptime(report_month, '%Y-%m-%d').date()
        
        # Check if user already has a report for this month (only if we have a user)
        if hasattr(self, 'user') and self.user:
            existing_report = MonthlyReport.objects.filter(
                employee=self.user,
                report_date=report_date
            ).first()
            
            if existing_report:
                raise ValidationError(
                    f"You have already submitted a report for {report_date.strftime('%B %Y')}. "
                    f"Submitted on {existing_report.submitted_at.strftime('%B %d, %Y at %I:%M %p')}."
                )
        
        return report_month

class AppraisalForm(forms.ModelForm):
    class Meta:
        model = Appraisal
        fields = ['score', 'comments']
        widgets = {
            'score': forms.NumberInput(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent', 'min': '1', 'max': '5'}),
            'comments': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent', 'rows': '4'}),
        }

class AttendanceForm(forms.ModelForm):
    class Meta:
        model = Attendance
        fields = ['note']
        widgets = {
            'note': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-primary focus:border-transparent', 'rows': '4', 'placeholder': 'Add any notes about your check-in today...'}),
        }
