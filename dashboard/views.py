import json
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from datetime import timedelta
from inventory.models import Product, Category, ProductBatch
from activity.models import ActivityLog
from django.db.models import Sum, Count


@login_required
def dashboard(request):
    today      = timezone.now().date()
    seven_days = today + timedelta(days=7)

    active_products = Product.objects.filter(is_active=True)

    total_products = active_products.count()
    low_stock      = active_products.filter(status='Low Stock').count()
    out_of_stock   = active_products.filter(status='Out of Stock').count()

    # Batch-aware expiration counts
    expiring_soon = (ProductBatch.objects
                     .filter(product__is_active=True, expiry_date__range=[today, seven_days])
                     .values('product').distinct().count())
    expired       = (ProductBatch.objects
                     .filter(product__is_active=True, expiry_date__lt=today)
                     .values('product').distinct().count())

    recent_products = active_products.select_related('category').order_by('-date_added')[:4]
    recent_logs     = ActivityLog.objects.select_related('product', 'user').order_by('-date')[:4]

    # Bar chart: stock quantity per category (uses synced quantity field)
    categories = Category.objects.all()
    bar_labels, bar_data = [], []
    for cat in categories:
        total_qty = active_products.filter(category=cat).aggregate(t=Sum('quantity'))['t'] or 0
        bar_labels.append(cat.name)
        bar_data.append(total_qty)

    in_stock_count = active_products.filter(status='In Stock').count()
    pie_data   = [in_stock_count, low_stock, out_of_stock]
    pie_labels = ['In Stock', 'Low Stock', 'Out of Stock']

    # Popup alerts
    popup_alerts = []
    if out_of_stock > 0:
        oos_names = list(active_products.filter(status='Out of Stock').values_list('name', flat=True)[:5])
        popup_alerts.append({'type': 'danger',  'title': f'{out_of_stock} Product(s) Out of Stock!',        'items': oos_names})
    if low_stock > 0:
        ls_names  = list(active_products.filter(status='Low Stock').values_list('name', flat=True)[:5])
        popup_alerts.append({'type': 'warning', 'title': f'{low_stock} Product(s) Low on Stock!',           'items': ls_names})
    if expired > 0:
        exp_batch_products = (ProductBatch.objects
                              .filter(product__is_active=True, expiry_date__lt=today)
                              .values_list('product__name', flat=True).distinct()[:5])
        popup_alerts.append({'type': 'danger',  'title': f'{expired} Product(s) Have Expired Batches!',     'items': list(exp_batch_products)})
    if expiring_soon > 0:
        es_batch_products  = (ProductBatch.objects
                              .filter(product__is_active=True, expiry_date__range=[today, seven_days])
                              .values_list('product__name', flat=True).distinct()[:5])
        popup_alerts.append({'type': 'warning', 'title': f'{expiring_soon} Product(s) Have Batches Expiring Soon!', 'items': list(es_batch_products)})

    context = {
        'total_products': total_products,
        'low_stock':      low_stock,
        'out_of_stock':   out_of_stock,
        'expiring_soon':  expiring_soon,
        'expired':        expired,
        'recent_products': recent_products,
        'recent_logs':     recent_logs,
        'today':           today,
        'bar_labels':  json.dumps(bar_labels),
        'bar_data':    json.dumps(bar_data),
        'pie_labels':  json.dumps(pie_labels),
        'pie_data':    json.dumps(pie_data),
        'popup_alerts': json.dumps(popup_alerts),
    }
    return render(request, 'dashboard.html', context)
