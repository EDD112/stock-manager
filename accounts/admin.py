from django.contrib import admin
from .models import UserProfile, Notification, NotificationRead, NotificationDismissed


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'is_account_active', 'created_at')
    list_filter = ('role', 'is_account_active')


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'notification_type', 'created_at')
    list_filter = ('notification_type',)


@admin.register(NotificationRead)
class NotificationReadAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification', 'read_at')
    list_filter = ('user',)


@admin.register(NotificationDismissed)
class NotificationDismissedAdmin(admin.ModelAdmin):
    list_display = ('user', 'notification', 'dismissed_at')
    list_filter = ('user',)
