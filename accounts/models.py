from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """Extends the built-in User model with a role field."""
    ROLE_CHOICES = (
        ('manager', 'Manager'),
        ('stockman', 'Stockman'),
    )
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='stockman')
    is_account_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

    def __str__(self):
        return f"{self.user.username} ({self.get_role_display()})"

    @property
    def is_manager(self):
        return self.role == 'manager'

    @property
    def is_stockman(self):
        return self.role == 'stockman'


class Notification(models.Model):
    """System-generated notifications for inventory conditions."""
    TYPE_CHOICES = (
        ('expired', 'Expired Product'),
        ('low_stock', 'Low Stock'),
        ('out_of_stock', 'Out of Stock'),
        ('expiring_soon', 'Expiring Soon'),
    )
    notification_type = models.CharField(max_length=20, choices=TYPE_CHOICES)
    title = models.CharField(max_length=255)
    message = models.TextField()
    product_name = models.CharField(max_length=200, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)
    # Unique key prevents duplicate notifications for the same condition
    unique_key = models.CharField(max_length=255, unique=True, blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'

    def __str__(self):
        return f"[{self.get_notification_type_display()}] {self.title}"


class NotificationRead(models.Model):
    """Tracks which user has read which notification (per-user read status)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='read_notifications')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='reads')
    read_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'notification')
        verbose_name = 'Notification Read'
        verbose_name_plural = 'Notification Reads'

    def __str__(self):
        return f"{self.user.username} read: {self.notification.title}"


class NotificationDismissed(models.Model):
    """Tracks which user has dismissed/cleared which notification (per-user clear)."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='dismissed_notifications')
    notification = models.ForeignKey(Notification, on_delete=models.CASCADE, related_name='dismissals')
    dismissed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'notification')
        verbose_name = 'Notification Dismissed'
        verbose_name_plural = 'Notification Dismissals'

    def __str__(self):
        return f"{self.user.username} dismissed: {self.notification.title}"


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Auto-create a profile when a new User is created."""
    if created:
        # Superusers are automatically Managers
        role = 'manager' if instance.is_superuser else 'stockman'
        UserProfile.objects.get_or_create(user=instance, defaults={'role': role})
