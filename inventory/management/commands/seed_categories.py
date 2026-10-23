from django.core.management.base import BaseCommand
from inventory.models import CategoryType

DEFAULTS = [
    ('Beverage', '#3b82f6', 'fa-wine-bottle'),
    ('Freezer', '#06b6d4', 'fa-snowflake'),
    ('Condiment', '#ef4444', 'fa-pepper-hot'),
    ('Dairy', '#f59e0b', 'fa-cheese'),
    ('Canned', '#8b5cf6', 'fa-cookie'),
    ('Snack', '#ec4899', 'fa-cookie-bite'),
    ('Bakery', '#f97316', 'fa-bread-slice'),
    ('Meat', '#dc2626', 'fa-drumstick-bite'),
    ('Seafood', '#0d9488', 'fa-fish'),
    ('Produce', '#10b981', 'fa-apple-alt'),
    ('Other', '#6b7280', 'fa-box'),
]


class Command(BaseCommand):
    help = 'Seed the default category types (safe to run repeatedly).'

    def handle(self, *args, **options):
        for name, color, icon in DEFAULTS:
            _, created = CategoryType.objects.get_or_create(
                name=name, defaults={'color': color, 'icon': icon})
            self.stdout.write(f"{'Created' if created else 'Exists'}: {name}")
