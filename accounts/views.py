from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.utils import timezone
from datetime import timedelta
from functools import wraps

from .models import UserProfile, Notification, NotificationRead, NotificationDismissed
from inventory.models import Product, ProductBatch


# ── DECORATORS ────────────────────────────────────────────────────────────


def get_user_role(user):
    """Return the user's role string. Creates profile if missing."""
    profile, created = UserProfile.objects.get_or_create(
        user=user,
        defaults={'role': 'manager' if user.is_superuser else 'stockman'}
    )
    return profile.role


def manager_required(view_func):
    """Decorator that restricts a view to Manager-role users only."""
    @wraps(view_func)
    @login_required
    def wrapper(request, *args, **kwargs):
        if get_user_role(request.user) != 'manager':
            messages.error(request, 'Access denied. This section is for Managers only.')
            return redirect('dashboard')
        return view_func(request, *args, **kwargs)
    return wrapper


# ── AUTH VIEWS ────────────────────────────────────────────────────────────


def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            # Check if the account has been deactivated by a manager
            profile, _ = UserProfile.objects.get_or_create(
                user=user,
                defaults={'role': 'manager' if user.is_superuser else 'stockman'}
            )
            if not profile.is_account_active:
                messages.error(request, 'Your account has been deactivated. Contact a Manager.')
                return render(request, 'registration/login.html')

            login(request, user)
            # ── Log the login ─────────────────────────────
            try:
                from login_tracker.models import LoginActivity
                ip = request.META.get('HTTP_X_FORWARDED_FOR', '').split(',')[0].strip() \
                     or request.META.get('REMOTE_ADDR')
                ua = request.META.get('HTTP_USER_AGENT', '')[:300]
                activity = LoginActivity.objects.create(
                    user=user,
                    ip_address=ip,
                    user_agent=ua,
                    session_key=request.session.session_key,
                )
                request.session['login_activity_id'] = activity.pk
            except Exception:
                pass
            next_url = request.GET.get('next', 'dashboard')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'registration/login.html')


@login_required
def logout_view(request):
    try:
        from login_tracker.models import LoginActivity
        activity_id = request.session.get('login_activity_id')
        if activity_id:
            LoginActivity.objects.filter(pk=activity_id).update(logout_time=timezone.now())
    except Exception:
        pass
    logout(request)
    return redirect('login')


@login_required
def toggle_dark_mode(request):
    """Toggle dark mode preference stored in session."""
    current = request.session.get('dark_mode', False)
    request.session['dark_mode'] = not current
    next_url = request.META.get('HTTP_REFERER', '/')
    return redirect(next_url)


# ── USER MANAGEMENT (Manager only) ───────────────────────────────────────


@manager_required
def manage_users(request):
    """List all user accounts (Manager dashboard)."""
    users = User.objects.select_related('profile').all().order_by('-date_joined')
    context = {'managed_users': users}
    return render(request, 'accounts/manage_users.html', context)


@manager_required
def create_stockman(request):
    """Create a new Stockman account."""
    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '').strip()
        confirm = request.POST.get('confirm_password', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        if not username or not password:
            messages.error(request, 'Username and password are required.')
            return render(request, 'accounts/create_stockman.html')

        if password != confirm:
            messages.error(request, 'Passwords do not match.')
            return render(request, 'accounts/create_stockman.html')

        if User.objects.filter(username=username).exists():
            messages.error(request, f'Username "{username}" already exists.')
            return render(request, 'accounts/create_stockman.html')

        user = User.objects.create_user(
            username=username,
            password=password,
            first_name=first_name,
            last_name=last_name,
        )
        # Signal creates the profile; ensure it's stockman
        profile, _ = UserProfile.objects.get_or_create(user=user, defaults={'role': 'stockman'})
        profile.role = 'stockman'
        profile.save()

        messages.success(request, f'Stockman account "{username}" created successfully.')
        return redirect('manage_users')

    return render(request, 'accounts/create_stockman.html')


@manager_required
def toggle_user_status(request, user_id):
    """Activate/Deactivate a user account."""
    target_user = get_object_or_404(User, pk=user_id)
    if target_user == request.user:
        messages.error(request, 'You cannot deactivate your own account.')
        return redirect('manage_users')

    profile, _ = UserProfile.objects.get_or_create(
        user=target_user,
        defaults={'role': 'manager' if target_user.is_superuser else 'stockman'}
    )
    profile.is_account_active = not profile.is_account_active
    profile.save()

    # Also toggle Django's is_active so they can't log in
    target_user.is_active = profile.is_account_active
    target_user.save(update_fields=['is_active'])

    status = 'activated' if profile.is_account_active else 'deactivated'
    messages.success(request, f'Account "{target_user.username}" has been {status}.')
    return redirect('manage_users')


@manager_required
def reset_user_password(request, user_id):
    """Reset a user's password."""
    target_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        new_password = request.POST.get('new_password', '').strip()
        confirm = request.POST.get('confirm_password', '').strip()

        if not new_password:
            messages.error(request, 'Password cannot be empty.')
            return redirect('manage_users')

        if new_password != confirm:
            messages.error(request, 'Passwords do not match.')
            return redirect('manage_users')

        target_user.set_password(new_password)
        target_user.save()
        messages.success(request, f'Password for "{target_user.username}" has been reset.')

    return redirect('manage_users')


@manager_required
def edit_user_profile(request, user_id):
    """Edit a user's profile details (username, first name, last name)."""
    target_user = get_object_or_404(User, pk=user_id)
    if request.method == 'POST':
        new_username = request.POST.get('username', '').strip()
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        if not new_username:
            messages.error(request, 'Username cannot be empty.')
            return redirect('manage_users')

        # Check if the new username is taken by another user
        if User.objects.filter(username=new_username).exclude(pk=target_user.pk).exists():
            messages.error(request, f'Username "{new_username}" is already taken by another user.')
            return redirect('manage_users')

        target_user.username = new_username
        target_user.first_name = first_name
        target_user.last_name = last_name
        target_user.save(update_fields=['username', 'first_name', 'last_name'])

        messages.success(request, f'Profile for "{new_username}" has been updated.')

    return redirect('manage_users')


# ── EDIT PROFILE (all users) ─────────────────────────────────────────────


@login_required
def edit_profile(request):
    """Allow any user to edit their own first name and last name."""
    if request.method == 'POST':
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()

        request.user.first_name = first_name
        request.user.last_name = last_name
        request.user.save(update_fields=['first_name', 'last_name'])

        messages.success(request, 'Your profile has been updated.')
        return redirect('edit_profile')

    return render(request, 'accounts/edit_profile.html')


@login_required
def change_own_password(request):
    """Allow any user to change their own password."""
    if request.method == 'POST':
        current = request.POST.get('current_password', '').strip()
        new_pw = request.POST.get('new_password', '').strip()
        confirm = request.POST.get('confirm_password', '').strip()

        if not request.user.check_password(current):
            messages.error(request, 'Current password is incorrect.')
            return redirect('edit_profile')

        if not new_pw:
            messages.error(request, 'New password cannot be empty.')
            return redirect('edit_profile')

        if new_pw != confirm:
            messages.error(request, 'New passwords do not match.')
            return redirect('edit_profile')

        request.user.set_password(new_pw)
        request.user.save()
        # Re-login so session doesn't expire
        login(request, request.user)
        messages.success(request, 'Your password has been changed.')
        return redirect('edit_profile')

    return redirect('edit_profile')


# ── NOTIFICATION SYSTEM ──────────────────────────────────────────────────


def generate_notifications():
    """Scan inventory and create notifications for conditions that need attention.
    Uses unique_key to avoid duplicating already-created notifications."""
    today = timezone.now().date()
    seven_days = today + timedelta(days=7)

    active_products = Product.objects.filter(is_active=True)

    # Out of stock
    for p in active_products.filter(status='Out of Stock'):
        key = f"out_of_stock_{p.pk}"
        Notification.objects.get_or_create(
            unique_key=key,
            defaults={
                'notification_type': 'out_of_stock',
                'title': f'{p.name} is Out of Stock',
                'message': f'{p.name} has 0 units remaining.',
                'product_name': p.name,
            }
        )

    # Low stock
    for p in active_products.filter(status='Low Stock'):
        key = f"low_stock_{p.pk}_{p.quantity}"
        Notification.objects.get_or_create(
            unique_key=key,
            defaults={
                'notification_type': 'low_stock',
                'title': f'{p.name} is Low on Stock',
                'message': f'{p.name} has only {p.quantity} units left.',
                'product_name': p.name,
            }
        )

    # Expired batches
    expired_batches = ProductBatch.objects.filter(
        expiry_date__lt=today, product__is_active=True
    ).select_related('product')
    for batch in expired_batches:
        key = f"expired_batch_{batch.pk}"
        Notification.objects.get_or_create(
            unique_key=key,
            defaults={
                'notification_type': 'expired',
                'title': f'{batch.product.name} – Batch #{batch.pk} has Expired',
                'message': f'Batch #{batch.pk} of {batch.product.name} expired on {batch.expiry_date}.',
                'product_name': batch.product.name,
            }
        )

    # Expiring soon batches
    expiring_batches = ProductBatch.objects.filter(
        expiry_date__range=[today, seven_days], product__is_active=True
    ).select_related('product')
    for batch in expiring_batches:
        key = f"expiring_soon_batch_{batch.pk}"
        Notification.objects.get_or_create(
            unique_key=key,
            defaults={
                'notification_type': 'expiring_soon',
                'title': f'{batch.product.name} – Batch #{batch.pk} Expiring Soon',
                'message': f'Batch #{batch.pk} of {batch.product.name} expires on {batch.expiry_date}.',
                'product_name': batch.product.name,
            }
        )


@login_required
def notification_list_api(request):
    """AJAX endpoint: return notifications as JSON for the bell dropdown."""
    # Generate fresh notifications on each check
    generate_notifications()

    role = get_user_role(request.user)
    notifications = Notification.objects.all()

    # Stockman can only see inventory-related notifications
    if role == 'stockman':
        notifications = notifications.filter(
            notification_type__in=['expired', 'low_stock', 'out_of_stock', 'expiring_soon']
        )

    # Exclude notifications this user has dismissed/cleared
    dismissed_ids = set(
        NotificationDismissed.objects.filter(user=request.user)
        .values_list('notification_id', flat=True)
    )
    notifications = notifications.exclude(pk__in=dismissed_ids)

    # Get the IDs this user has already read
    read_ids = set(
        NotificationRead.objects.filter(user=request.user)
        .values_list('notification_id', flat=True)
    )

    unread_count = notifications.exclude(pk__in=read_ids).count()
    recent = notifications[:30]

    data = {
        'unread_count': unread_count,
        'role': role,
        'notifications': [
            {
                'id': n.pk,
                'type': n.notification_type,
                'title': n.title,
                'message': n.message,
                'is_read': n.pk in read_ids,
                'created_at': n.created_at.strftime('%b %d, %Y %I:%M %p'),
            }
            for n in recent
        ]
    }
    return JsonResponse(data)


@login_required
def mark_notification_read(request, notif_id):
    """Mark a single notification as read for the current user."""
    NotificationRead.objects.get_or_create(user=request.user, notification_id=notif_id)
    return JsonResponse({'status': 'ok'})


@login_required
def mark_all_notifications_read(request):
    """Mark all visible notifications as read for the current user only."""
    role = get_user_role(request.user)
    notifications = Notification.objects.all()

    if role == 'stockman':
        notifications = notifications.filter(
            notification_type__in=['expired', 'low_stock', 'out_of_stock', 'expiring_soon']
        )

    # Get IDs this user hasn't read yet
    already_read = set(
        NotificationRead.objects.filter(user=request.user)
        .values_list('notification_id', flat=True)
    )
    unread = notifications.exclude(pk__in=already_read)

    # Bulk create read records
    NotificationRead.objects.bulk_create(
        [NotificationRead(user=request.user, notification_id=n.pk) for n in unread],
        ignore_conflicts=True,
    )
    return JsonResponse({'status': 'ok'})


@login_required
def clear_all_notifications(request):
    """Dismiss all visible notifications for the current user only."""
    role = get_user_role(request.user)
    notifications = Notification.objects.all()

    if role == 'stockman':
        notifications = notifications.filter(
            notification_type__in=['expired', 'low_stock', 'out_of_stock', 'expiring_soon']
        )

    # Exclude already dismissed
    already_dismissed = set(
        NotificationDismissed.objects.filter(user=request.user)
        .values_list('notification_id', flat=True)
    )
    to_dismiss = notifications.exclude(pk__in=already_dismissed)

    NotificationDismissed.objects.bulk_create(
        [NotificationDismissed(user=request.user, notification_id=n.pk) for n in to_dismiss],
        ignore_conflicts=True,
    )
    return JsonResponse({'status': 'ok', 'message': 'All notifications cleared for your account.'})
