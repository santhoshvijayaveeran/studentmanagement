"""
Email service for sending notifications
"""
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from django.template import TemplateDoesNotExist, TemplateSyntaxError
import logging

logger = logging.getLogger(__name__)


def send_notification_email(notification):
    """
    Send email notification asynchronously.
    
    Args:
        notification: Notification model instance
        
    Returns:
        bool: True if sent successfully, False otherwise
    """
    try:
        # Get recipient email
        recipient_email = notification.recipient.email
        if not recipient_email:
            logger.warning(f"No email address for user {notification.recipient.username}")
            notification.mark_as_failed("No email address on file")
            return False
        
        # Prepare email content
        subject = notification.subject
        text_content = notification.message
        
        # Try to render HTML template if available
        try:
            context = {
                'recipient_name': notification.recipient.get_full_name() or notification.recipient.username,
                'subject': subject,
                'message': notification.message,
                'notification_type': notification.get_notification_type_display(),
            }
            html_content = render_to_string('email_notifications/notification_email.html', context)
        except (TemplateDoesNotExist, TemplateSyntaxError):
            html_content = None
        
        # Send email
        if html_content:
            email = EmailMultiAlternatives(
                subject=subject,
                body=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                to=[recipient_email]
            )
            email.attach_alternative(html_content, "text/html")
            email.send()
        else:
            send_mail(
                subject=subject,
                message=text_content,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[recipient_email],
                fail_silently=False
            )
        
        # Mark as sent
        notification.mark_as_sent()
        logger.info(f"Notification sent to {recipient_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send notification {notification.id}: {str(e)}")
        notification.mark_as_failed(str(e))
        return False


def send_grade_released_email(grade):
    """
    Send email when a grade is released.
    
    Args:
        grade: Grade model instance
    """
    from .models import Notification
    
    try:
        enrollment = grade.enrollment
        student_user = enrollment.student.user
        
        if not student_user:
            logger.warning(f"No user associated with student {enrollment.student}")
            return False
        
        subject = f"Grade Released for {enrollment.course.code}"
        message = f"""
Hello {student_user.get_full_name()},

Your grade for {enrollment.course.code} ({enrollment.course.name}) has been released.

Grade: {grade.grade}
Marks: {grade.marks}/{100}
Percentage: {grade.percentage}%

Please log in to your portal to view your full transcript.

Best regards,
Academic Management System
        """.strip()
        
        # Create notification
        notification = Notification.objects.create(
            recipient=student_user,
            notification_type='grade_released',
            subject=subject,
            message=message,
            related_grade=grade
        )
        
        # Send email
        return send_notification_email(notification)
        
    except Exception as e:
        logger.error(f"Error sending grade released email: {str(e)}")
        return False


def send_fee_due_email(fee):
    """
    Send email when a fee is due soon.
    
    Args:
        fee: Fee model instance
    """
    from .models import Notification
    from datetime import timedelta
    from django.utils import timezone
    
    try:
        # Only send if due date is within 7 days
        days_until_due = (fee.due_date - timezone.now().date()).days
        if days_until_due > 7 or days_until_due < 0:
            return False
        
        student_user = fee.student.user
        if not student_user:
            logger.warning(f"No user associated with student {fee.student}")
            return False
        
        subject = f"Fee Due: {fee.fee_type} - Due on {fee.due_date.strftime('%B %d, %Y')}"
        message = f"""
Hello {student_user.get_full_name()},

This is a reminder that your {fee.fee_type} fee is due soon.

Fee Details:
- Type: {fee.fee_type}
- Amount: ${fee.amount}
- Due Date: {fee.due_date.strftime('%B %d, %Y')}
- Status: {fee.get_status_display()}

Please submit your payment before the due date to avoid late fees.

Best regards,
Academic Management System
        """.strip()
        
        notification = Notification.objects.create(
            recipient=student_user,
            notification_type='fee_due',
            subject=subject,
            message=message,
            related_fee=fee
        )
        
        return send_notification_email(notification)
        
    except Exception as e:
        logger.error(f"Error sending fee due email: {str(e)}")
        return False


def send_fee_overdue_email(fee):
    """
    Send email when a fee becomes overdue.
    
    Args:
        fee: Fee model instance
    """
    from .models import Notification
    from django.utils import timezone
    
    try:
        if fee.due_date >= timezone.now().date():
            return False  # Not overdue yet
        
        student_user = fee.student.user
        if not student_user:
            logger.warning(f"No user associated with student {fee.student}")
            return False
        
        days_overdue = (timezone.now().date() - fee.due_date).days
        
        subject = f"URGENT: Overdue Fee - {fee.fee_type}"
        message = f"""
Hello {student_user.get_full_name()},

Your {fee.fee_type} fee is now OVERDUE.

Fee Details:
- Type: {fee.fee_type}
- Amount: ${fee.amount}
- Due Date: {fee.due_date.strftime('%B %d, %Y')}
- Days Overdue: {days_overdue}

Immediate payment is required. Please contact the accounts department for details on late fees.

Best regards,
Academic Management System
        """.strip()
        
        notification = Notification.objects.create(
            recipient=student_user,
            notification_type='fee_overdue',
            subject=subject,
            message=message,
            related_fee=fee
        )
        
        return send_notification_email(notification)
        
    except Exception as e:
        logger.error(f"Error sending fee overdue email: {str(e)}")
        return False


def send_enrollment_confirmed_email(enrollment):
    """
    Send email when enrollment is confirmed.
    
    Args:
        enrollment: Enrollment model instance
    """
    from .models import Notification
    
    try:
        student_user = enrollment.student.user
        if not student_user:
            logger.warning(f"No user associated with student {enrollment.student}")
            return False
        
        subject = f"Enrollment Confirmed: {enrollment.course.code}"
        message = f"""
Hello {student_user.get_full_name()},

Your enrollment has been confirmed for the following course:

Course: {enrollment.course.code} - {enrollment.course.name}
Instructor: {enrollment.course.instructor.user.get_full_name()}
Credits: {enrollment.course.credits}
Semester: {enrollment.semester}

Enrollment Date: {enrollment.enrollment_date.strftime('%B %d, %Y')}

Welcome to the course! Please check your portal for course materials and updates.

Best regards,
Academic Management System
        """.strip()
        
        notification = Notification.objects.create(
            recipient=student_user,
            notification_type='enrollment_confirmed',
            subject=subject,
            message=message,
            related_enrollment=enrollment
        )
        
        return send_notification_email(notification)
        
    except Exception as e:
        logger.error(f"Error sending enrollment confirmed email: {str(e)}")
        return False


def send_attendance_warning_email(student_user, course, attendance_percentage):
    """
    Send email for low attendance warning.
    
    Args:
        student_user: User instance (student)
        course: Course instance
        attendance_percentage: Float percentage
    """
    from .models import Notification
    
    try:
        subject = f"Attendance Warning: {course.code}"
        message = f"""
Hello {student_user.get_full_name()},

This is a warning that your attendance in {course.code} ({course.name}) is low.

Current Attendance: {attendance_percentage}%
Minimum Required: 75%

Please make effort to attend classes regularly. Continued low attendance may affect your academic standing.

If you have any issues, please contact your course instructor: {course.instructor.user.get_full_name()}

Best regards,
Academic Management System
        """.strip()
        
        notification = Notification.objects.create(
            recipient=student_user,
            notification_type='attendance_warning',
            subject=subject,
            message=message
        )
        
        return send_notification_email(notification)
        
    except Exception as e:
        logger.error(f"Error sending attendance warning email: {str(e)}")
        return False


def send_academic_warning_email(transcript):
    """
    Send email for academic standing warning.
    
    Args:
        transcript: Transcript model instance
    """
    from .models import Notification
    
    try:
        student_user = transcript.student.user
        if not student_user:
            logger.warning(f"No user associated with student {transcript.student}")
            return False
        
        subject = "Academic Standing Alert"
        message = f"""
Hello {student_user.get_full_name()},

Your current academic standing is: {transcript.get_academic_standing_display()}

Performance Summary:
- Cumulative GPA: {transcript.cumulative_gpa}/4.0
- Courses Passed: {transcript.total_courses_passed}
- Courses Failed: {transcript.total_courses_failed}

If your standing drops to Probation, you may face academic restrictions.

Please meet with your academic advisor to discuss your progress and plan your next semester.

Best regards,
Academic Management System
        """.strip()
        
        notification = Notification.objects.create(
            recipient=student_user,
            notification_type='academic_warning',
            subject=subject,
            message=message
        )
        
        return send_notification_email(notification)
        
    except Exception as e:
        logger.error(f"Error sending academic warning email: {str(e)}")
        return False
