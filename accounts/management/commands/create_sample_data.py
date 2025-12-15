from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from accounts.models import School
import random


class Command(BaseCommand):
    help = 'Creates sample schools and users for testing role-based access'

    def handle(self, *args, **options):
        User = get_user_model()
        
        # Create sample schools
        schools_data = [
            {'name': 'Central High School', 'address': '123 Main St, Downtown'},
            {'name': 'Riverside Elementary', 'address': '456 River Rd, Riverside'},
            {'name': 'Oakwood Academy', 'address': '789 Oak Ave, Oakwood'},
            {'name': 'Lincoln Middle School', 'address': '321 Lincoln Blvd, Midtown'},
        ]
        
        schools = []
        for school_data in schools_data:
            school, created = School.objects.get_or_create(
                name=school_data['name'],
                defaults=school_data
            )
            schools.append(school)
            if created:
                self.stdout.write(self.style.SUCCESS(f'Created school: {school.name}'))
        
        # Create admin users
        admin_users_data = [
            {'username': 'admin1', 'email': 'admin1@school.edu', 'first_name': 'Alice', 'last_name': 'Johnson'},
            {'username': 'admin2', 'email': 'admin2@school.edu', 'first_name': 'Bob', 'last_name': 'Smith'},
        ]
        
        for i, user_data in enumerate(admin_users_data):
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': 'administration',
                    'school': schools[i % len(schools)],
                }
            )
            if created:
                user.set_password('admin123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created admin user: {user.username}'))
        
        # Create education users
        education_users_data = [
            {'username': 'teacher1', 'email': 'teacher1@school.edu', 'first_name': 'Carol', 'last_name': 'Davis'},
            {'username': 'teacher2', 'email': 'teacher2@school.edu', 'first_name': 'David', 'last_name': 'Wilson'},
            {'username': 'teacher3', 'email': 'teacher3@school.edu', 'first_name': 'Emma', 'last_name': 'Brown'},
        ]
        
        for user_data in education_users_data:
            user, created = User.objects.get_or_create(
                username=user_data['username'],
                defaults={
                    'email': user_data['email'],
                    'first_name': user_data['first_name'],
                    'last_name': user_data['last_name'],
                    'role': 'education',
                }
            )
            if created:
                user.set_password('teacher123')
                user.save()
                self.stdout.write(self.style.SUCCESS(f'Created education user: {user.username}'))
        
        # Display summary
        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write(self.style.WARNING('\nLogin credentials:'))
        self.stdout.write('Admin users:')
        self.stdout.write('  - admin1 / admin123')
        self.stdout.write('  - admin2 / admin123')
        self.stdout.write('Education users:')
        self.stdout.write('  - teacher1 / teacher123')
        self.stdout.write('  - teacher2 / teacher123')
        self.stdout.write('  - teacher3 / teacher123')