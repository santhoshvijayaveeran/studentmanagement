"""Global template context available on every page (used by the shared
nav shell in templates/base.html)."""

from .models import Notification


def nav_context(request):
    """Provide sidebar/header data: unread notification count for the
    logged-in user. Kept cheap (single count query) since it runs on
    every request."""
    unread_notifications = 0
    user = getattr(request, 'user', None)
    if user is not None and user.is_authenticated:
        unread_notifications = Notification.objects.filter(
            recipient=user, is_read=False
        ).count()
    return {
        'nav_unread_notifications': unread_notifications,
    }
