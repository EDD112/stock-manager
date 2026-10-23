import os
from pathlib import Path

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent

# --- Environment-driven config (set these in Vercel > Settings > Environment Variables) ---
# DEBUG defaults to True locally; set DJANGO_DEBUG=False in production.
DEBUG = os.environ.get('DJANGO_DEBUG', 'True').lower() in ('1', 'true', 'yes')
SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-change-this-in-production-use-env-variable',
)
if not DEBUG and SECRET_KEY.startswith('django-insecure'):
    raise RuntimeError('Set DJANGO_SECRET_KEY in the environment when DJANGO_DEBUG is False.')

ALLOWED_HOSTS = ['*']

CSRF_TRUSTED_ORIGINS = ['https://*.vercel.app']
# Optional: your custom domain(s), comma-separated, e.g. https://stock.example.com
CSRF_TRUSTED_ORIGINS += [
    o.strip() for o in os.environ.get('CSRF_EXTRA_ORIGINS', '').split(',') if o.strip()
]

# Vercel terminates HTTPS and forwards the original scheme in this header.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

if DEBUG:
    # Trust HTTPS connections from local network (for runsecure command)
    CSRF_TRUSTED_ORIGINS += ['https://localhost:8443', 'https://127.0.0.1:8443']
    for _i in range(256):
        CSRF_TRUSTED_ORIGINS.append(f'https://192.168.0.{_i}:8443')
        CSRF_TRUSTED_ORIGINS.append(f'https://192.168.1.{_i}:8443')
        CSRF_TRUSTED_ORIGINS.append(f'https://10.0.0.{_i}:8443')
else:
    SESSION_COOKIE_SECURE = True
    CSRF_COOKIE_SECURE = True

INSTALLED_APPS = [
    'jazzmin',
    'dashboard',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    # local apps
    'accounts',
    'inventory',
    'activity',
    'expiration',
    'login_tracker',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'inventory_system.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'accounts.context_processors.user_profile',
            ],
        },
    },
]

WSGI_APPLICATION = 'inventory_system.wsgi.application'

# Vercel's filesystem is read-only/ephemeral, so production needs a hosted Postgres
# (Neon, Supabase, Vercel Postgres...). Set DATABASE_URL. Without it, local SQLite is used.
_db_url = os.environ.get('DATABASE_URL') or os.environ.get('POSTGRES_URL')
if _db_url:
    DATABASES = {'default': dj_database_url.parse(_db_url, conn_max_age=0)}
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': BASE_DIR / 'db.sqlite3',
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Asia/Manila'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATICFILES_DIRS = [BASE_DIR / 'static'] if (BASE_DIR / 'static').exists() else []
STATIC_ROOT = BASE_DIR / 'staticfiles'
# Serve admin/Jazzmin static files straight from the installed packages (no collectstatic needed).
WHITENOISE_USE_FINDERS = True
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

LOGIN_URL = '/accounts/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/accounts/login/'

JAZZMIN_SETTINGS = {
    "site_title": "Inventory Admin",
    "site_header": "StockManager Admin",
    "site_brand": "StockManager",
    "welcome_sign": "Welcome to StockManager Admin",
    "copyright": "StockManager System",
    "search_model": ["inventory.Product", "auth.User"],
    "topmenu_links": [
        {"name": "Dashboard", "url": "/", "new_window": True},
    ],
    "show_sidebar": True,
    "navigation_expanded": True,
    "icons": {
        "auth":                     "fas fa-users-cog",
        "auth.user":                "fas fa-user",
        "auth.Group":               "fas fa-users",
        "inventory.Product":        "fas fa-box",
        "inventory.Category":       "fas fa-tags",
        "activity.ActivityLog":     "fas fa-history",
        "login_tracker.LoginActivity": "fas fa-sign-in-alt",
    },
    "default_icon_parents": "fas fa-chevron-circle-right",
    "default_icon_children": "fas fa-circle",
    "related_modal_active": False,
    "show_ui_builder": False,
    "changeform_format": "horizontal_tabs",
    "theme": "darkly",
    "dark_mode_theme": "darkly",
}
