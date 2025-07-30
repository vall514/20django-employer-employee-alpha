from django.shortcuts import render, redirect, get_object_or_404
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
        # Calculate department performance
        department_performance = 0
        if user.department:
            department_performance = user.department.calculate_performance_score()
        
        context = {
            'leave_requests': LeaveRequest.objects.filter(employee__department=user.department, status='pending'),
            'employees': User.objects.filter(department=user.department, role='employee'),
            'department_performance': department_performance,
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
def leave_approve_list_view(request):
    user = request.user
    if user.role == 'hod':
        leave_requests = LeaveRequest.objects.filter(employee__department=user.department, status='pending')
        return render(request, 'core/leave_approve_hod.html', {
            'leave_requests': leave_requests,
            'user': user
        })
    elif user.role == 'hr':
        leave_requests = LeaveRequest.objects.filter(status='hod_approved')
        return render(request, 'core/leave_approve_hr.html', {
            'leave_requests': leave_requests,
            'user': user
        })
    else:
        messages.error(request, 'Unauthorized access.')
        return redirect('core:dashboard')

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
    
    # Redirect back to the appropriate leave approval page instead of dashboard
    if request.user.role == 'hod':
        return redirect('core:leave_approve_list')
    elif request.user.role == 'hr':
        return redirect('core:leave_approve_list')
    return redirect('core:dashboard')

@login_required
def monthly_report_view(request):
    if request.user.role != 'employee':
        messages.error(request, 'Only employees can submit reports.')
        return redirect('core:dashboard')
    
    from .forms import MonthlyReportForm
    
    if request.method == 'POST':
        form = MonthlyReportForm(request.POST, request.FILES)
        form.user = request.user  # Pass user to form for validation
        if form.is_valid():
            try:
                report = form.save(commit=False)
                report.employee = request.user
                report.save()
                
                # Success message with submission details
                report_month = report.report_date.strftime('%B %Y')
                submitted_time = report.submitted_at.strftime('%B %d, %Y at %I:%M %p')
                on_time_status = "on time" if report.is_submitted_on_time() else "late"
                
                messages.success(
                    request, 
                    f'Monthly report for {report_month} submitted successfully {on_time_status} on {submitted_time}!'
                )
                return redirect('core:dashboard')
            except Exception as e:
                messages.error(request, f'Error submitting report: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = MonthlyReportForm()
        form.user = request.user  # Pass user to form for validation
    
    return render(request, 'core/monthly_report.html', {'form': form})

@login_required
def appraisal_list_view(request):
    if request.user.role != 'hod':
        messages.error(request, 'Only HODs can access appraisal management.')
        return redirect('core:dashboard')
    
    employees = User.objects.filter(department=request.user.department, role='employee')
    return render(request, 'core/appraisal_list.html', {
        'employees': employees,
        'user': request.user
    })

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
        return redirect('core:appraisal_list')
    return render(request, 'core/appraisal_form.html', {'employee': employee})

@login_required
def attendance_check_in(request):
    if request.user.role != 'employee':
        messages.error(request, 'Only employees can check in.')
        return redirect('core:dashboard')
    
    from .forms import AttendanceForm
    from django.utils import timezone
    import pytz
    
    # Check if user already checked in today
    nairobi_tz = pytz.timezone('Africa/Nairobi')
    today = timezone.now().astimezone(nairobi_tz).date()
    
    existing_attendance = Attendance.objects.filter(
        employee=request.user, 
        date=today
    ).first()
    
    if existing_attendance:
        messages.warning(request, f'You have already checked in today at {existing_attendance.check_in_time.astimezone(nairobi_tz).strftime("%I:%M %p")}.')
        return redirect('core:dashboard')
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST)
        if form.is_valid():
            try:
                now_nairobi = timezone.now().astimezone(nairobi_tz)
                attendance = form.save(commit=False)
                attendance.employee = request.user
                attendance.date = today
                attendance.check_in_time = now_nairobi
                attendance.save()  # This will automatically calculate status
                
                formatted_time = now_nairobi.strftime('%I:%M:%S %p')
                formatted_date = now_nairobi.strftime('%B %d, %Y')
                status_text = "on time" if attendance.status == 'on_time' else "late"
                status_color = "success" if attendance.status == 'on_time' else "warning"
                
                messages.add_message(
                    request, 
                    getattr(messages, status_color.upper()),
                    f'Checked in {status_text} on {formatted_date} at {formatted_time} (Nairobi time).'
                )
                return redirect('core:dashboard')
            except Exception as e:
                messages.error(request, f'Error recording attendance: {str(e)}')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        form = AttendanceForm()
        
    # Add current time info for the template
    now_nairobi = timezone.now().astimezone(nairobi_tz)
    deadline = nairobi_tz.localize(
        timezone.datetime.combine(today, timezone.datetime.min.time().replace(hour=9))
    )
    
    context = {
        'form': form,
        'current_time': now_nairobi,
        'deadline': deadline,
        'is_late': now_nairobi > deadline
    }
    
    return render(request, 'core/attendance_check_in.html', context)

@login_required
def monthly_reports_list_view(request):
    if request.user.role not in ['hod', 'hr']:
        messages.error(request, 'Only HOD and HR can view monthly reports.')
        return redirect('core:dashboard')
    
    # Get reports based on user role
    if request.user.role == 'hod':
        # HOD can see reports from their department only
        reports = MonthlyReport.objects.filter(
            employee__department=request.user.department
        ).select_related('employee', 'employee__department')
    else:  # HR
        # HR can see all reports
        reports = MonthlyReport.objects.all().select_related('employee', 'employee__department')
    
    return render(request, 'core/monthly_reports_list.html', {
        'reports': reports,
        'user': request.user
    })

@login_required
def attendance_list_view(request):
    if request.user.role not in ['hod', 'hr']:
        messages.error(request, 'Only HOD and HR can view attendance records.')
        return redirect('core:dashboard')
    
    from django.utils import timezone
    from datetime import datetime
    
    # Get current date
    today = timezone.now().date()
    selected_date = request.GET.get('date', str(today))
    
    try:
        filter_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        filter_date = today
    
    # Get attendance records based on user role
    if request.user.role == 'hod':
        # HOD can see attendance from their department only
        all_employees = User.objects.filter(
            department=request.user.department, role='employee'
        ).select_related('employeeprofile')
    else:  # HR
        # HR can see all employees
        all_employees = User.objects.filter(role='employee').select_related('employeeprofile')
    
    # Get attendance records for the selected date
    attendance_records = []
    for employee in all_employees:
        try:
            attendance = Attendance.objects.get(employee=employee, date=filter_date)
        except Attendance.DoesNotExist:
            # Create a placeholder for absent employees
            attendance = Attendance(
                employee=employee,
                date=filter_date,
                status='absent',
                check_in_time=None,
                note=''
            )
        attendance_records.append(attendance)
    
    # Apply status filter if provided
    status_filter = request.GET.get('status')
    if status_filter:
        attendance_records = [a for a in attendance_records if a.status == status_filter]
    
    # Calculate statistics for the selected date
    on_time_count = sum(1 for a in attendance_records if a.status == 'on_time')
    late_count = sum(1 for a in attendance_records if a.status == 'late')
    absent_count = sum(1 for a in attendance_records if a.status == 'absent')
    total_employees = len(all_employees)
    
    stats = {
        'on_time_count': on_time_count,
        'late_count': late_count,
        'absent_count': absent_count,
        'total_employees': total_employees,
    }
    
    return render(request, 'core/attendance_list.html', {
        'attendance_records': attendance_records,
        'selected_date': filter_date,
        'selected_status': status_filter,
        'stats': stats,
    })

@login_required
def employee_attendance_detail(request, employee_id):
    if request.user.role == 'employee' and request.user.id != employee_id:
        messages.error(request, 'You can only view your own attendance.')
        return redirect('core:dashboard')
    elif request.user.role == 'hod':
        employee = get_object_or_404(User, id=employee_id, department=request.user.department)
    elif request.user.role == 'hr':
        employee = get_object_or_404(User, id=employee_id)
    else:
        employee = request.user
    
    from datetime import datetime, timedelta
    
    # Get attendance data for the last 30 days
    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=30)
    
    attendance_records = Attendance.objects.filter(
        employee=employee,
        date__range=[start_date, end_date]
    ).order_by('-date')
    
    # Calculate statistics
    total_days = (end_date - start_date).days + 1
    present_days = attendance_records.count()
    on_time_count = attendance_records.filter(status='on_time').count()
    late_count = attendance_records.filter(status='late').count()
    absent_count = total_days - present_days
    
    # Create weekly pattern data (last 7 days)
    weekly_pattern = []
    today = datetime.now().date()
    for i in range(7):
        day_date = today - timedelta(days=6-i)
        day_record = attendance_records.filter(date=day_date).first()
        if day_record:
            weekly_pattern.append({
                'status': day_record.status,
                'count': 1,
                'date': day_date
            })
        else:
            weekly_pattern.append({
                'status': 'absent',
                'count': 0,
                'date': day_date
            })
    
    return render(request, 'core/employee_attendance_detail.html', {
        'employee': employee,
        'recent_records': attendance_records[:20],  # Show last 20 records
        'stats': {
            'total_days': present_days,  # Only count actual attendance records
            'on_time_count': on_time_count,
            'late_count': late_count,
            'absent_count': absent_count,
            'attendance_rate': round((present_days / total_days) * 100, 1),
            'punctuality_rate': round((on_time_count / present_days) * 100, 1) if present_days > 0 else 0,
        },
        'weekly_pattern': weekly_pattern,
        'user': request.user
    })

@login_required
def department_attendance_view(request):
    """HR view for department-wise attendance overview"""
    if request.user.role != 'hr':
        messages.error(request, 'Only HR can access department attendance.')
        return redirect('core:dashboard')
    
    from employees.models import Department
    from django.utils import timezone
    from datetime import datetime, timedelta
    from django.db.models import Count, Q
    
    # Get current date and selected date
    today = timezone.now().date()
    selected_date = request.GET.get('date', str(today))
    selected_department = request.GET.get('department', '')
    
    try:
        filter_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        filter_date = today
    
    # Get all departments
    departments = Department.objects.all()
    
    # Calculate department statistics
    department_stats = []
    for dept in departments:
        if selected_department and dept.name != selected_department:
            continue
            
        employees = User.objects.filter(department=dept, role='employee')
        total_employees = employees.count()
        
        if total_employees == 0:
            continue
        
        # Get attendance for this department on selected date
        attendance_records = Attendance.objects.filter(
            employee__department=dept,
            date=filter_date
        )
        
        on_time = attendance_records.filter(status='on_time').count()
        late = attendance_records.filter(status='late').count()
        present = attendance_records.count()
        absent = total_employees - present
        
        # Calculate performance score
        performance_score = dept.calculate_performance_score()
        
        department_stats.append({
            'department': dept,
            'total_employees': total_employees,
            'on_time': on_time,
            'late': late,
            'absent': absent,
            'present': present,
            'attendance_rate': round((present / total_employees) * 100, 1) if total_employees > 0 else 0,
            'punctuality_rate': round((on_time / present) * 100, 1) if present > 0 else 0,
            'performance_score': performance_score,
        })
    
    # Calculate overall statistics
    total_stats = {
        'total_employees': sum(d['total_employees'] for d in department_stats),
        'total_on_time': sum(d['on_time'] for d in department_stats),
        'total_late': sum(d['late'] for d in department_stats),
        'total_absent': sum(d['absent'] for d in department_stats),
    }
    
    context = {
        'department_stats': department_stats,
        'total_stats': total_stats,
        'departments': departments,
        'selected_date': filter_date,
        'selected_department': selected_department,
    }
    
    return render(request, 'core/department_attendance.html', context)

@login_required
def download_department_attendance(request):
    """Download attendance for HOD's department as CSV"""
    if request.user.role != 'hod':
        messages.error(request, 'Only HOD can download department attendance.')
        return redirect('core:dashboard')
    
    if not request.user.department:
        messages.error(request, 'You are not assigned to any department.')
        return redirect('core:attendance_list')
    
    import csv
    from django.http import HttpResponse
    from django.utils import timezone
    from datetime import datetime, timedelta
    
    # Get date range (default to current month)
    today = timezone.now().date()
    start_date = request.GET.get('start_date', str(today.replace(day=1)))
    end_date = request.GET.get('end_date', str(today))
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start_date = today.replace(day=1)
        end_date = today
    
    # Get all employees in HOD's department
    employees = User.objects.filter(
        department=request.user.department,
        role='employee'
    ).order_by('first_name', 'last_name')
    
    # Create HTTP response with CSV content
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_{request.user.department.get_name_display()}_{start_date}_to_{end_date}.csv"'
    
    writer = csv.writer(response)
    
    # Write header
    writer.writerow([
        'Employee Name',
        'Email',
        'Date',
        'Check-in Time',
        'Status',
        'Note'
    ])
    
    # Write attendance data
    for employee in employees:
        attendance_records = Attendance.objects.filter(
            employee=employee,
            date__range=[start_date, end_date]
        ).order_by('date')
        
        if attendance_records:
            for record in attendance_records:
                writer.writerow([
                    employee.get_full_name(),
                    employee.email,
                    record.date.strftime('%Y-%m-%d'),
                    record.check_in_time.strftime('%H:%M:%S') if record.check_in_time else '',
                    record.get_status_display(),
                    record.note or ''
                ])
        else:
            # Add a row for employees with no attendance records
            writer.writerow([
                employee.get_full_name(),
                employee.email,
                'No attendance records',
                '',
                '',
                ''
            ])
    
    return response