from django.core.management.base import BaseCommand
from employees.models import Department

class Command(BaseCommand):
    help = 'Create default departments'

    def handle(self, *args, **options):
        departments = [
            'communication',
            'creatives', 
            'tech_department',
            'community_experience',
            'youth_engagement',
            'heritage',
            'admin',
            'finance',
            'entrepreneurship',
        ]
        
        created_count = 0
        for dept_name in departments:
            department, created = Department.objects.get_or_create(name=dept_name)
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created department: {department.get_name_display()}')
                )
            else:
                self.stdout.write(f'Department already exists: {department.get_name_display()}')
        
        self.stdout.write(
            self.style.SUCCESS(f'Created {created_count} new departments')
        )
