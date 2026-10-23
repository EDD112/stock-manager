from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from inventory.models import ProductBatch


@login_required
def expiration_tracker(request):
    today      = timezone.now().date()
    seven_days = today + timedelta(days=7)

    # Now batch-aware: query batches, not products
    expired_batches  = (ProductBatch.objects
                        .filter(expiry_date__lt=today, product__is_active=True)
                        .select_related('product', 'product__category')
                        .order_by('expiry_date'))

    expiring_batches = (ProductBatch.objects
                        .filter(expiry_date__range=[today, seven_days], product__is_active=True)
                        .select_related('product', 'product__category')
                        .order_by('expiry_date'))

    context = {
        'expired_batches':  expired_batches,
        'expiring_batches': expiring_batches,
        'today': today,
    }
    return render(request, 'expiration/expiration_tracker.html', context)
