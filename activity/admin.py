from django.contrib import admin
from .models import ActivityLog


@admin.register(ActivityLog)
class ActivityLogAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'action', 'quantity', 'notes', 'date')
    list_filter = ('action', 'user')
    search_fields = ('product__name', 'user__username')
    readonly_fields = ('date',)
