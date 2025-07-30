from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from employees.models import Department
from core.models import EmployeeProfile

User = get_user_model()

class Command(BaseCommand):
    help = 'Create a test user for development'

    def handle(self, *args, **options):
        # Create test user
        if not User.objects.filter(username='testuser').exists():
            user = User.objects.create_user(
                username='testuser',
                email='test@example.com',
                password='testpass123',
                first_name='Test',
                last_name='User',
                role='employee',
                email_verified=True
            )
            
            # Create department if doesn't exist
            department, created = Department.objects.get_or_create(
                name='IT',
                defaults={'description': 'Information Technology Department'}
            )
            
            # Create employee profile
            EmployeeProfile.objects.get_or_create(
                user=user,
                defaults={
                    'department': department,
                    'employee_id': 'EMP001',
                    'phone_number': '1234567890'
                }
            )
            
            self.stdout.write(
                self.style.SUCCESS(f'Successfully created test user: testuser / testpass123')
            )
        else:
            self.stdout.write(
                self.style.WARNING('Test user already exists')
            )
