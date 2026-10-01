"""
Django signals for automatic notification triggers
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
from datetime import timedelta
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender='students.Grade')
def notify_grade_released(sender, instance, created, **kwargs):
    """Send notification when a grade is released."""
    from .email_service import send_grade_released_email
    
    if instance.released:
        try:
            send_grade_released_email(instance)
        except Exception as e:
            logger.error(f"Error in grade release signal: {str(e)}")


@receiver(post_save, sender='students.Fee')
def check_fee_due(sender, instance, created, **kwargs):
    """Send notification for fees due soon or overdue."""
    from .email_service import send_fee_due_email, send_fee_overdue_email
    from .models import Notification
    
    try:
        today = timezone.now().date()
        
        # Check if overdue
        if instance.due_date < today and instance.status != 'paid':
            # Only send if we haven't sent an overdue notification recently
            recent_overdue = Notification.objects.filter(
                related_fee=instance,
                notification_type='fee_overdue',
                created_at__gte=timezone.now() - timedelta(days=7)
            ).exists()
            if not recent_overdue:
                send_fee_overdue_email(instance)
        
        # Check if due soon
        elif instance.due_date <= today + timedelta(days=7) and instance.status != 'paid':
            # Only send if we haven't sent a due notification recently
            recent_due = Notification.objects.filter(
                related_fee=instance,
                notification_type='fee_due',
                created_at__gte=timezone.now() - timedelta(days=1)
            ).exists()
            if not recent_due:
                send_fee_due_email(instance)
                
    except Exception as e:
        logger.error(f"Error in fee check signal: {str(e)}")


@receiver(post_save, sender='students.Enrollment')
def notify_enrollment_confirmed(sender, instance, created, **kwargs):
    """Send notification when enrollment is confirmed."""
    from .email_service import send_enrollment_confirmed_email
    
    if created:
        try:
            send_enrollment_confirmed_email(instance)
        except Exception as e:
            logger.error(f"Error in enrollment signal: {str(e)}")


@receiver(post_save, sender='students.Transcript')
def check_academic_standing(sender, instance, created, update_fields, **kwargs):
    """Send notification for academic standing changes."""
    from .email_service import send_academic_warning_email
    from .models import Notification
    
    try:
        # Check if standing changed to warning level
        if instance.academic_standing in ['Satisfactory', 'Probation']:
            # Only send if we haven't sent recently
            recent_warning = Notification.objects.filter(
                related_grade__isnull=True,  # ID trick to find transcript notifications
                notification_type='academic_warning',
                recipient=instance.student.user,
                created_at__gte=timezone.now() - timedelta(days=30)
            ).exists()
            if not recent_warning:
                send_academic_warning_email(instance)
                
    except Exception as e:
        logger.error(f"Error in transcript signal: {str(e)}")


def setup_signals():
    """Register all signals. Call this in apps.py ready() method."""
    pass  # Signals auto-register when this module is imported
