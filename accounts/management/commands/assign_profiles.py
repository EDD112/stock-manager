from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from accounts.models import UserProfile


class Command(BaseCommand):
    help = 'Create UserProfile for all existing users that do not have one.'

    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(profile__isnull=True)
        count = 0
        for user in users_without_profile:
            role = 'manager' if user.is_superuser else 'stockman'
            UserProfile.objects.create(user=user, role=role)
            count += 1
            self.stdout.write(f'  Created profile for "{user.username}" → {role}')
        self.stdout.write(self.style.SUCCESS(f'Done. {count} profile(s) created.'))
