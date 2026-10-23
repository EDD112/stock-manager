from django.db import models
from django.contrib.auth.models import User


class LoginActivity(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='login_activities')
    login_time = models.DateTimeField(auto_now_add=True)
    logout_time = models.DateTimeField(null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.CharField(max_length=300, blank=True, null=True)
    session_key = models.CharField(max_length=40, blank=True, null=True,
                                   help_text="Django session key – used to match logout to the correct login record.")

    class Meta:
        ordering = ['-login_time']
        verbose_name = 'Login Activity'
        verbose_name_plural = 'Login Activities'

    @property
    def duration(self):
        """Return session duration as a formatted string, or None if still active."""
        if self.logout_time and self.login_time:
            delta = self.logout_time - self.login_time
            total = int(delta.total_seconds())
            h, rem = divmod(total, 3600)
            m, s = divmod(rem, 60)
            if h:
                return f"{h}h {m}m"
            elif m:
                return f"{m}m {s}s"
            return f"{s}s"
        return None

    def __str__(self):
        return f"{self.user.username} — {self.login_time.strftime('%Y-%m-%d %H:%M')}"
