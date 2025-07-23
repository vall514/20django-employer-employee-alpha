from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import User
from employees.models import Department
from core.models import EmployeeProfile

# Create your views here.
def register_view(request):
    departments = Department.objects.all()
    if request.method == 'POST':
        username = request.POST.get('username')
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        password = request.POST.get('password')
        role = request.POST.get('role')
        department_id = request.POST.get('department')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'accounts/register.html', {'departments': departments})
        
        user = User.objects.create_user(
            username=username,
            first_name=first_name,
            last_name=last_name,
            email=email,
            password=password,
            role=role
        )
        if department_id:
            user.department = Department.objects.get(id=department_id)
        user.save()
        messages.success(request, 'Registration successful. Please log in.')
        return redirect('accounts:login')
    
    return render(request, 'accounts/register.html', {'departments': departments})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return render(request, 'accounts/login.html')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return render(request, 'accounts/logout.html')

@login_required
def profile_view(request):
    profile, created = EmployeeProfile.objects.get_or_create(user=request.user)
    departments = Department.objects.all()
    if request.method == 'POST':
        profile.phone = request.POST.get('phone', '')
        profile.address = request.POST.get('address', '')
        profile.date_of_birth = request.POST.get('date_of_birth', None)
        department_id = request.POST.get('department')
        if department_id:
            request.user.department = Department.objects.get(id=department_id)
        request.user.save()
        profile.save()
        messages.success(request, 'Profile updated successfully.')
        return redirect('core:dashboard')
    return render(request, 'accounts/profile.html', {'profile': profile, 'departments': departments})