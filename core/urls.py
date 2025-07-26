from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('leave/request/', views.leave_request_view, name='leave_request'),
    path('leave/approve-list/', views.leave_approve_list_view, name='leave_approve_list'),
    path('leave/approve/<int:leave_id>/', views.leave_approve_view, name='leave_approve'),
    path('report/submit/', views.monthly_report_view, name='monthly_report'),
    path('appraisal/list/', views.appraisal_list_view, name='appraisal_list'),
    path('appraisal/submit/<int:employee_id>/', views.appraisal_view, name='appraisal'),
    path('attendance/check-in/', views.attendance_check_in, name='attendance_check_in'),
]