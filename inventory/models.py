from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User


class CategoryType(models.Model):
    """User-defined category types (Beverage, Freezer, Condiment, or anything custom)."""

    ICON_CHOICES = (
        ('fa-wine-bottle',  'Bottle (Beverage)'),
        ('fa-snowflake',    'Snowflake (Freezer)'),
        ('fa-pepper-hot',   'Pepper (Condiment)'),
        ('fa-cheese',       'Cheese (Dairy)'),
        ('fa-cookie',       'Cookie (Canned/Tin)'),
        ('fa-cookie-bite',  'Cookie Bite (Snack)'),
        ('fa-bread-slice',  'Bread (Bakery)'),
        ('fa-drumstick-bite','Drumstick (Meat)'),
        ('fa-fish',         'Fish (Seafood)'),
        ('fa-apple-alt',    'Apple (Produce)'),
        ('fa-seedling',     'Seedling (Organic)'),
        ('fa-coffee',       'Coffee (Hot Drinks)'),
        ('fa-ice-cream',    'Ice Cream (Frozen Desserts)'),
        ('fa-carrot',       'Carrot (Vegetables)'),
        ('fa-box',          'Box (General/Other)'),
        ('fa-tags',         'Tag (Misc)'),
    )

    COLOR_CHOICES = (
        ('#3b82f6', 'Blue'),
        ('#06b6d4', 'Cyan'),
        ('#ef4444', 'Red'),
        ('#f59e0b', 'Yellow/Amber'),
        ('#8b5cf6', 'Purple'),
        ('#ec4899', 'Pink'),
        ('#f97316', 'Orange'),
        ('#10b981', 'Green'),
        ('#6b7280', 'Gray'),
        ('#dc2626', 'Dark Red'),
        ('#0d9488', 'Teal'),
        ('#7c3aed', 'Violet'),
    )

    name  = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default='#6b7280', choices=COLOR_CHOICES)
    icon  = models.CharField(max_length=50, default='fa-box', choices=ICON_CHOICES)

    class Meta:
        ordering = ['name']
        verbose_name = 'Category Type'
        verbose_name_plural = 'Category Types'

    def __str__(self):
        return self.name


class Category(models.Model):
    name          = models.CharField(max_length=100, unique=True)
    category_type = models.ForeignKey(
        CategoryType,
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='categories'
    )
    description    = models.CharField(max_length=255, blank=True, null=True)
    is_active      = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    @property
    def icon(self):
        return self.category_type.icon if self.category_type else 'fa-box'

    @property
    def color(self):
        return self.category_type.color if self.category_type else '#6b7280'

    @property
    def type_name(self):
        return self.category_type.name if self.category_type else 'Uncategorized'

    def deactivate(self):
        """Soft-delete category and cascade-deactivate all its products."""
        self.is_active = False
        self.deactivated_at = timezone.now()
        self.save()
        self.products.filter(is_active=True).update(
            is_active=False, deactivated_at=timezone.now()
        )

    def restore(self):
        """Restore category and all products that were deactivated with it."""
        self.is_active = True
        self.deactivated_at = None
        self.save()
        # Restore products whose deactivated_at is close to this category's deactivation time
        # (i.e., products deactivated by this category's soft-delete, not manually)
        self.products.filter(is_active=False).update(
            is_active=True, deactivated_at=None
        )

    def __str__(self):
        return f"{self.name} ({self.type_name})"


class Product(models.Model):
    STATUS_CHOICES = (
        ('In Stock',     'In Stock'),
        ('Low Stock',    'Low Stock'),
        ('Out of Stock', 'Out of Stock'),
    )

    name           = models.CharField(max_length=200, unique=True)
    category       = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, related_name='products')
    quantity       = models.IntegerField(default=0)
    expiry_date    = models.DateField()
    status         = models.CharField(max_length=50, choices=STATUS_CHOICES, editable=False, default='In Stock')
    is_active      = models.BooleanField(default=True)
    deactivated_at = models.DateTimeField(null=True, blank=True)
    date_added     = models.DateTimeField(auto_now_add=True)
    last_updated   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['name']

    def save(self, *args, **kwargs):
        if self.quantity == 0:
            self.status = 'Out of Stock'
        elif self.quantity < 10:
            self.status = 'Low Stock'
        else:
            self.status = 'In Stock'
        super().save(*args, **kwargs)

    @property
    def total_quantity(self):
        """Sum of all active batch quantities."""
        return sum(b.quantity for b in self.batches.all())

    def sync_quantity(self):
        """Sync the product's quantity field with the sum of all batches."""
        self.quantity = self.total_quantity
        self.save()

    def deactivate(self):
        self.is_active = False
        self.deactivated_at = timezone.now()
        self.save()

    def restore(self):
        self.is_active = True
        self.deactivated_at = None
        self.save()

    @property
    def earliest_expiry(self):
        """Dynamically return the earliest expiry date from remaining batches."""
        batch = self.batches.order_by('expiry_date').first()
        return batch.expiry_date if batch else self.expiry_date

    def sync_expiry(self):
        """Update the product's expiry_date to match the earliest remaining batch."""
        batch = self.batches.order_by('expiry_date').first()
        if batch and batch.expiry_date != self.expiry_date:
            self.expiry_date = batch.expiry_date
            self.save(update_fields=['expiry_date', 'last_updated'])

    def is_expired(self):
        return self.earliest_expiry < timezone.now().date()

    def is_expiring_soon(self):
        today = timezone.now().date()
        from datetime import timedelta
        return today <= self.earliest_expiry <= today + timedelta(days=7)

    def __str__(self):
        return self.name


class ProductBatch(models.Model):
    """Represents a distinct stock batch for a product with its own expiry date."""
    product     = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='batches')
    quantity    = models.IntegerField(default=0)
    expiry_date = models.DateField()
    added_by    = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    date_added  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['date_added', 'id']  # True FIFO: oldest created batch first, regardless of expiry
        verbose_name = 'Product Batch'
        verbose_name_plural = 'Product Batches'

    def is_expired(self):
        return self.expiry_date < timezone.now().date()

    def is_expiring_soon(self):
        from datetime import timedelta
        today = timezone.now().date()
        return today <= self.expiry_date <= today + timedelta(days=7)

    def __str__(self):
        return f"{self.product.name} | Batch #{self.pk} | Qty: {self.quantity} | Exp: {self.expiry_date}"
