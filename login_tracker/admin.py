from django.contrib import admin
from .models import LoginActivity


@admin.register(LoginActivity)
class LoginActivityAdmin(admin.ModelAdmin):
    list_display = ('user', 'login_time', 'ip_address')
    list_filter = ('user',)
    readonly_fields = ('user', 'login_time', 'ip_address', 'user_agent')
    ordering = ('-login_time',)
