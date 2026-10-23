from accounts.models import UserProfile


def user_profile(request):
    """Ensure the user always has a profile attached, so templates can use request.user.profile."""
    if request.user.is_authenticated:
        profile, created = UserProfile.objects.get_or_create(
            user=request.user,
            defaults={'role': 'manager' if request.user.is_superuser else 'stockman'}
        )
    return {}
