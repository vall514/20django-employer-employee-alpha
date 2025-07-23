from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import LeaveRequest, MonthlyReport, Appraisal, Attendance
from accounts.models import User
from employees.models import Department

# Create your views here.
def home_view(request):
    return render(request, 'core/home.html')

@login_required
def dashboard_view(request):
    user = request.user
    if user.role == 'employee':
        template = 'core/dashboard_employee.html'
        context = {
            'leave_requests': LeaveRequest.objects.filter(employee=user),
            'reports': MonthlyReport.objects.filter(employee=user),
            'appraisals': Appraisal.objects.filter(employee=user),
            'attendance': Attendance.objects.filter(employee=user),
        }
    elif user.role == 'hod':
        template = 'core/dashboard_hod.html'
        context = {
            'leave_requests': LeaveRequest.objects.filter(employee__department=user.department, status='pending'),
            'employees': User.objects.filter(department=user.department, role='employee'),
        }
    else:  # HR
        template = 'core/dashboard_hr.html'
        context = {
            'leave_requests': LeaveRequest.objects.filter(status='hod_approved'),
            'all_employees': User.objects.all(),
            'reports': MonthlyReport.objects.all(),
            'appraisals': Appraisal.objects.all(),
            'attendance': Attendance.objects.all(),
        }
    context['user'] = user  # Ensure user is available for sidebar
    return render(request, template, context)

@login_required
def leave_request_view(request):
    if request.user.role != 'employee':
        messages.error(request, 'Only employees can request leaves.')
        return redirect('core:dashboard')
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        LeaveRequest.objects.create(
            employee=request.user,
            start_date=start_date,
            end_date=end_date,
            reason=reason
        )
        messages.success(request, 'Leave request submitted.')
        return redirect('core:dashboard')
    return render(request, 'core/leave_request.html')

@login_required
def leave_approve_view(request, leave_id):
    leave = LeaveRequest.objects.get(id=leave_id)
    if request.user.role == 'hod' and leave.employee.department == request.user.department:
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'approve':
                leave.hod_approval = True
                leave.status = 'hod_approved'
            else:
                leave.status = 'rejected'
            leave.save()
            messages.success(request, f'Leave request {action}d.')
    elif request.user.role == 'hr':
        if request.method == 'POST':
            action = request.POST.get('action')
            if action == 'approve':
                leave.hr_approval = True
                leave.status = 'hr_approved'
            else:
                leave.status = 'rejected'
            leave.save()
            messages.success(request, f'Leave request {action}d.')
    else:
        messages.error(request, 'Unauthorized action.')
    return redirect('core:dashboard')

@login_required
def monthly_report_view(request):
    if request.user.role != 'employee':
        messages.error(request, 'Only employees can submit reports.')
        return redirect('core:dashboard')
    if request.method == 'POST':
        month = request.POST.get('month')
        file = request.FILES.get('file')
        description = request.POST.get('description')
        MonthlyReport.objects.create(
            employee=request.user,
            month=month,
            file=file,
            description=description
        )
        messages.success(request, 'Report submitted.')
        return redirect('core:dashboard')
    return render(request, 'core/monthly_report.html')

@login_required
def appraisal_view(request, employee_id):
    if request.user.role != 'hod':
        messages.error(request, 'Only HODs can submit appraisals.')
        return redirect('core:dashboard')
    employee = User.objects.get(id=employee_id)
    if employee.department != request.user.department:
        messages.error(request, 'Unauthorized action.')
        return redirect('core:dashboard')
    if request.method == 'POST':
        score = request.POST.get('score')
        comments = request.POST.get('comments')
        Appraisal.objects.create(
            employee=employee,
            evaluator=request.user,
            score=score,
            comments=comments
        )
        messages.success(request, 'Appraisal submitted.')
        return redirect('core:dashboard')
    return render(request, 'core/appraisal_form.html', {'employee': employee})

@login_required
def attendance_check_in(request):
    if request.user.role != 'employee':
        messages.error(request, 'Only employees can check in.')
        return redirect('core:dashboard')
    if request.method == 'POST':
        note = request.POST.get('note', '')
        Attendance.objects.create(employee=request.user, note=note)
        messages.success(request, 'Checked in successfully.')
        return redirect('core:dashboard')
    return render(request, 'core/attendance_check_in.html')