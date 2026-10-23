#!/bin/bash
echo "========================================"
echo "  StockManager v3 — Setup Script"
echo "========================================"

echo "[1/5] Installing dependencies..."
pip install -r requirements.txt

echo "[2/5] Running migrations..."
python manage.py makemigrations accounts activity login_tracker
python manage.py migrate

echo "[3/5] Creating Manager account..."
echo "       You will be asked for username, first name, last name, and password."
python manage.py createsuperuser

echo "       Assigning profiles to all users..."
python manage.py assign_profiles

echo "[4/5] Seeding default category types..."
python manage.py shell -c "
from inventory.models import CategoryType
defaults = [
    ('Beverage',  '#3b82f6', 'fa-wine-bottle'),
    ('Freezer',   '#06b6d4', 'fa-snowflake'),
    ('Condiment', '#ef4444', 'fa-pepper-hot'),
    ('Dairy',     '#f59e0b', 'fa-cheese'),
    ('Canned',    '#8b5cf6', 'fa-cookie'),
    ('Snack',     '#ec4899', 'fa-cookie-bite'),
    ('Bakery',    '#f97316', 'fa-bread-slice'),
    ('Meat',      '#dc2626', 'fa-drumstick-bite'),
    ('Seafood',   '#0d9488', 'fa-fish'),
    ('Produce',   '#10b981', 'fa-apple-alt'),
    ('Other',     '#6b7280', 'fa-box'),
]
for name, color, icon in defaults:
    ct, created = CategoryType.objects.get_or_create(name=name, defaults={'color': color, 'icon': icon})
    print(f'  {\"Created\" if created else \"Exists\"}: {name}')
"

echo "[5/5] Setup complete!"
echo ""
echo "========================================"
echo "  HOW TO RUN:"
echo ""
echo "  Normal (PC only):"
echo "    python manage.py runserver 0.0.0.0:8000"
echo "    Open: http://127.0.0.1:8000/"
echo ""
echo "  HTTPS (for mobile sound/vibration):"
echo "    python manage.py runsecure"
echo "    Open on phone: https://<your-pc-ip>:8443/"
echo "    (Tap 'Advanced' > 'Proceed' on the warning)"
echo ""
echo "  Admin: http://127.0.0.1:8000/admin/"
echo "========================================"
