from django.db import models
from django.contrib.auth.models import User
from inventory.models import Product


class ActivityLog(models.Model):
    ACTION_CHOICES = (
        ('ADD', 'Added'),
        ('REMOVE', 'Removed'),
        ('UPDATE', 'Updated'),
        ('DELETE', 'Deleted'),
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.SET_NULL,   # preserve log even when product is deleted/deactivated
        null=True, blank=True,
        related_name='logs'
    )
    product_name = models.CharField(
        max_length=200, blank=True, default='',
        help_text="Snapshot of product name at log time – kept even if product is removed."
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=10, choices=ACTION_CHOICES)
    quantity = models.IntegerField(default=0)
    notes = models.CharField(max_length=255, blank=True, null=True)
    date = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = "Activity Log"
        verbose_name_plural = "Activity Logs"

    def save(self, *args, **kwargs):
        # Auto-snapshot the product name so it survives product deletion
        if self.product and not self.product_name:
            self.product_name = self.product.name
        super().save(*args, **kwargs)

    def get_product_name(self):
        """Return the product name whether the product still exists or not."""
        if self.product:
            return self.product.name
        return self.product_name or '(Deleted Product)'

    def __str__(self):
        return f"{self.user.username} {self.get_action_display()} {self.get_product_name()} ({self.quantity})"
