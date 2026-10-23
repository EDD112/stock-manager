from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('dashboard.urls')),
    path('inventory/', include('inventory.urls')),
    path('activity/', include('activity.urls')),
    path('expiration/', include('expiration.urls')),
    path('accounts/', include('accounts.urls')),
    path('login-activity/', include('login_tracker.urls')),
]
