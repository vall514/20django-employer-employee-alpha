from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.urls import reverse
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
import re
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
        confirm_password = request.POST.get('confirm_password')
        role = request.POST.get('role')
        department_id = request.POST.get('department')
        
        # Validate form data
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return render(request, 'accounts/register_new.html', {'departments': departments})
        
        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return render(request, 'accounts/register_new.html', {'departments': departments})
        
        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/register_new.html', {'departments': departments})
        
        # Custom password validation
        try:
            # Check minimum length
            if len(password) < 8:
                raise ValidationError("Password must be at least 8 characters long.")
            
            # Check for at least one lowercase letter
            if not re.search(r'[a-z]', password):
                raise ValidationError("Password must contain at least one lowercase letter.")
            
            # Check for at least one uppercase letter
            if not re.search(r'[A-Z]', password):
                raise ValidationError("Password must contain at least one uppercase letter.")
            
            # Check for at least one digit
            if not re.search(r'\d', password):
                raise ValidationError("Password must contain at least one number.")
            
            # Check for at least one special character
            if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
                raise ValidationError("Password must contain at least one special character.")
            
            # Django's built-in password validation
            validate_password(password, User)
            
        except ValidationError as e:
            for error in e.messages:
                messages.error(request, error)
            return render(request, 'accounts/register_new.html', {'departments': departments})
        
        # Create user but set as inactive until email is verified
        try:
            user = User.objects.create_user(
                username=username,
                first_name=first_name,
                last_name=last_name,
                email=email,
                password=password,
                role=role,
                is_active=True,  # Keep active but use email_verified for restriction
                email_verified=False
            )
            if department_id:
                user.department = Department.objects.get(id=department_id)
            
            # Generate verification token
            token = user.generate_verification_token()
            user.save()
            
            # Create verification link
            verification_link = f"{settings.SITE_URL}{reverse('accounts:verify_email', args=[token])}"
            
            # Prepare email content
            html_message = render_to_string('accounts/verification_email.html', {
                'user': user,
                'verification_link': verification_link,
                'site_name': settings.SITE_NAME
            })
            plain_message = strip_tags(html_message)
            
            # Send email
            try:
                send_mail(
                    subject=f"Verify your email for {settings.SITE_NAME}",
                    message=plain_message,
                    from_email=settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'noreply@workpulse.com',
                    recipient_list=[email],
                    html_message=html_message,
                    fail_silently=False,
                )
                messages.success(request, 'Registration successful! Please check your email to verify your account before logging in.')
            except Exception as e:
                messages.warning(request, f'Account created but there was an issue sending the verification email. Please contact support.')
                
            return redirect('accounts:login')
        except Exception as e:
            messages.error(request, f'Error creating account: {str(e)}')
            return render(request, 'accounts/register_new.html', {'departments': departments})
    
    return render(request, 'accounts/register_new.html', {'departments': departments})

def verify_email_view(request, token):
    user = get_object_or_404(User, verification_token=token)
    
    if user.email_verified:
        messages.info(request, 'Your email has already been verified. You can log in.')
        return redirect('accounts:login')
    else:
        user.email_verified = True
        user.verification_token = None  # Clear the token after use
        user.save()
        return render(request, 'accounts/email_verified.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            # Check if email is verified
            if not user.email_verified:
                messages.error(request, 'Please verify your email before logging in. Check your inbox for the verification link.')
                return render(request, 'accounts/login.html')
                
            login(request, user)
            return redirect('core:dashboard')
        else:
            messages.error(request, 'Invalid credentials')
            return render(request, 'accounts/login.html')
    return render(request, 'accounts/login.html')

def logout_view(request):
    logout(request)
    return render(request, 'accounts/logout.html')

def resend_verification_email(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            user = User.objects.get(email=email)
            
            if user.email_verified:
                messages.info(request, 'Your email is already verified. You can log in.')
                return redirect('accounts:login')
                
            # Generate new verification token
            token = user.generate_verification_token()
            
            # Create verification link
            verification_link = f"{settings.SITE_URL}{reverse('accounts:verify_email', args=[token])}"
            
            # Prepare email content
            html_message = render_to_string('accounts/verification_email.html', {
                'user': user,
                'verification_link': verification_link,
                'site_name': settings.SITE_NAME
            })
            plain_message = strip_tags(html_message)
            
            # Send email
            send_mail(
                subject=f"Verify your email for {settings.SITE_NAME}",
                message=plain_message,
                from_email=settings.EMAIL_HOST_USER if hasattr(settings, 'EMAIL_HOST_USER') else 'noreply@workpulse.com',
                recipient_list=[email],
                html_message=html_message,
                fail_silently=False,
            )
            messages.success(request, 'Verification email has been resent. Please check your inbox.')
        except User.DoesNotExist:
            messages.error(request, 'No account exists with this email address.')
        except Exception as e:
            messages.error(request, 'There was an error sending the verification email. Please try again later.')
            
    return render(request, 'accounts/resend_verification.html')

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