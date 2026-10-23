"""
Custom createsuperuser that asks for username, first name, last name, and password.
No email required.

Usage: python manage.py createsuperuser
"""
import getpass
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Create a superuser (Manager) with username, first name, last name, and password.'

    def handle(self, *args, **options):
        self.stdout.write('\n  Create Manager Account')
        self.stdout.write('  ' + '=' * 30 + '\n')

        # Username
        while True:
            username = input('  Username: ').strip()
            if not username:
                self.stderr.write('  Error: Username cannot be blank.\n')
                continue
            if User.objects.filter(username=username).exists():
                self.stderr.write(f'  Error: Username "{username}" already exists.\n')
                continue
            break

        # First name
        first_name = input('  First name: ').strip()

        # Last name
        last_name = input('  Last name: ').strip()

        # Password
        while True:
            password = getpass.getpass('  Password: ')
            if not password:
                self.stderr.write('  Error: Password cannot be blank.\n')
                continue
            password2 = getpass.getpass('  Confirm password: ')
            if password != password2:
                self.stderr.write('  Error: Passwords do not match.\n')
                continue
            if len(password) < 4:
                self.stderr.write('  Error: Password must be at least 4 characters.\n')
                continue
            break

        user = User.objects.create_superuser(
            username=username,
            password=password,
            email='',
            first_name=first_name,
            last_name=last_name,
        )

        # Ensure profile is Manager
        profile, _ = UserProfile.objects.get_or_create(
            user=user, defaults={'role': 'manager'}
        )
        profile.role = 'manager'
        profile.save()

        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS(
            f'  Manager account created successfully!'
        ))
        self.stdout.write(f'  Username:  {username}')
        self.stdout.write(f'  Name:      {first_name} {last_name}')
        self.stdout.write(f'  Role:      Manager')
        self.stdout.write('')
