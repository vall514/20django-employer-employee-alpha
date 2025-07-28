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
    class Meta:
        model = MonthlyReport
        fields = ['month', 'description', 'file']
        widgets = {
            'month': forms.DateInput(attrs={'type': 'month', 'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-4 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-secondary focus:border-transparent', 'rows': '6'}),
            'file': forms.FileInput(attrs={'class': 'hidden', 'accept': '.pdf,.doc,.docx,.xls,.xlsx'}),
        }

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
