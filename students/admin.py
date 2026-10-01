from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import User, Faculty, Student, Department, Course, Enrollment, Attendance, Grade, Fee, Transcript, DegreeAudit, FacultyReport, Notification, Book, BookInstance, BorrowRecord, Classroom, TimetableSlot, Exam


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin configuration."""
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Additional Info', {'fields': ('role', 'phone', 'department', 'enrollment_year')}),
    )
    list_display = ('username', 'first_name', 'last_name', 'email', 'role', 'date_joined')
    list_filter = ('role', 'date_joined')
    search_fields = ('username', 'email', 'first_name', 'last_name')


@admin.register(Faculty)
class FacultyAdmin(admin.ModelAdmin):
    """Faculty admin configuration."""
    list_display = ('user', 'employee_id', 'department', 'experience_years', 'created_at')
    search_fields = ('user__first_name', 'user__last_name', 'employee_id', 'department')
    list_filter = ('department', 'created_at')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    """Student admin configuration."""
    list_display = ('name', 'roll_number', 'email', 'phone', 'department', 'enrollment_year', 'created_at')
    search_fields = ('name', 'roll_number', 'email', 'department')
    list_filter = ('department', 'enrollment_year', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    """Department admin configuration."""
    list_display = ('code', 'name', 'hod', 'total_seats', 'created_at')
    search_fields = ('code', 'name')
    list_filter = ('created_at',)
    readonly_fields = ('created_at',)


@admin.register(Course)
class CourseAdmin(admin.ModelAdmin):
    """Course admin configuration."""
    list_display = ('code', 'name', 'department', 'instructor', 'semester', 'credits', 'capacity')
    search_fields = ('code', 'name', 'department__name')
    list_filter = ('department', 'semester', 'credits', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Enrollment)
class EnrollmentAdmin(admin.ModelAdmin):
    """Enrollment admin configuration."""
    list_display = ('student', 'course', 'status', 'semester_year', 'enrollment_date')
    search_fields = ('student__name', 'course__code')
    list_filter = ('status', 'semester_year', 'enrollment_date')
    readonly_fields = ('enrollment_date',)


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    """Attendance admin configuration."""
    list_display = ('enrollment', 'date', 'status', 'recorded_by', 'created_at')
    search_fields = ('enrollment__student__name', 'enrollment__course__code')
    list_filter = ('status', 'date', 'created_at')
    readonly_fields = ('created_at',)


@admin.register(Grade)
class GradeAdmin(admin.ModelAdmin):
    """Grade admin configuration."""
    list_display = ('enrollment', 'total_marks', 'percentage', 'grade', 'released', 'released_date')
    search_fields = ('enrollment__student__name', 'enrollment__course__code')
    list_filter = ('grade', 'released', 'released_date')
    readonly_fields = ('total_marks', 'percentage', 'grade', 'released_date')


@admin.register(Fee)
class FeeAdmin(admin.ModelAdmin):
    """Fee admin configuration."""
    list_display = ('student', 'fee_type', 'amount', 'paid_amount', 'outstanding_amount', 'payment_status', 'due_date')
    search_fields = ('student__name', 'fee_type')
    list_filter = ('fee_type', 'payment_status', 'semester', 'year', 'due_date')
    readonly_fields = ('created_at',)
    ordering = ('-created_at',)


@admin.register(Transcript)
class TranscriptAdmin(admin.ModelAdmin):
    """Transcript admin configuration."""
    list_display = ('student', 'cumulative_gpa', 'total_credits_completed', 'cumulative_percentage', 'academic_standing', 'last_updated')
    search_fields = ('student__name', 'student__roll_number')
    list_filter = ('academic_standing', 'last_updated')
    readonly_fields = ('cumulative_gpa', 'total_credits_completed', 'total_credits_attempted', 'total_courses_passed', 'total_courses_failed', 'cumulative_percentage', 'academic_standing', 'last_updated', 'generated_date')
    fieldsets = (
        ('Student Information', {
            'fields': ('student',)
        }),
        ('Academic Performance', {
            'fields': ('cumulative_gpa', 'cumulative_percentage', 'academic_standing')
        }),
        ('Credits Summary', {
            'fields': ('total_credits_completed', 'total_credits_attempted')
        }),
        ('Courses Summary', {
            'fields': ('total_courses_passed', 'total_courses_failed')
        }),
        ('Timestamps', {
            'fields': ('generated_date', 'last_updated'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DegreeAudit)
class DegreeAuditAdmin(admin.ModelAdmin):
    """Degree Audit admin configuration."""
    list_display = ('student', 'degree_name', 'overall_progress', 'audit_status', 'expected_graduation', 'updated_at')
    search_fields = ('student__name', 'student__roll_number', 'degree_name')
    list_filter = ('audit_status', 'degree_name', 'updated_at')
    readonly_fields = ('core_courses_completed', 'elective_courses_completed', 'total_credits_earned', 'overall_progress', 'created_at', 'updated_at')
    fieldsets = (
        ('Degree Information', {
            'fields': ('student', 'degree_name')
        }),
        ('Credits Requirements', {
            'fields': ('total_credits_required', 'total_credits_earned', 'overall_progress')
        }),
        ('Course Requirements', {
            'fields': ('core_courses_required', 'core_courses_completed', 'elective_courses_required', 'elective_courses_completed')
        }),
        ('Status', {
            'fields': ('audit_status', 'expected_graduation')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FacultyReport)
class FacultyReportAdmin(admin.ModelAdmin):
    """Faculty Report admin configuration."""
    list_display = ('faculty', 'total_courses_taught', 'total_students_taught', 'average_class_gpa', 'pass_rate_percentage', 'last_updated')
    search_fields = ('faculty__user__first_name', 'faculty__user__last_name', 'faculty__employee_id')
    list_filter = ('last_updated',)
    readonly_fields = ('total_courses_taught', 'current_semester_courses', 'total_students_taught', 'current_semester_students', 
                       'average_class_gpa', 'average_grades_given', 'pass_rate_percentage', 'fail_rate_percentage',
                       'grade_a_count', 'grade_b_count', 'grade_c_count', 'grade_d_count', 'grade_f_count',
                       'total_credits_assigned', 'average_class_size', 'peak_semester_load', 'generated_date', 'last_updated')
    fieldsets = (
        ('Faculty Information', {
            'fields': ('faculty',)
        }),
        ('Course Statistics', {
            'fields': ('total_courses_taught', 'current_semester_courses', 'total_students_taught', 'current_semester_students')
        }),
        ('Grade Statistics', {
            'fields': ('average_class_gpa', 'average_grades_given', 'pass_rate_percentage', 'fail_rate_percentage')
        }),
        ('Grade Distribution', {
            'fields': ('grade_a_count', 'grade_b_count', 'grade_c_count', 'grade_d_count', 'grade_f_count')
        }),
        ('Workload Analysis', {
            'fields': ('total_credits_assigned', 'average_class_size', 'peak_semester_load')
        }),
        ('Student Satisfaction', {
            'fields': ('student_satisfaction_score',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('generated_date', 'last_updated'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Notification admin configuration."""
    list_display = ('recipient', 'notification_type', 'subject', 'email_sent', 'is_read', 'created_at')
    list_filter = ('notification_type', 'email_sent', 'is_read', 'created_at')
    search_fields = ('recipient__username', 'recipient__email', 'subject', 'message')
    readonly_fields = ('created_at', 'sent_at', 'read_at', 'failure_reason')
    
    fieldsets = (
        ('Recipient & Type', {
            'fields': ('recipient', 'notification_type')
        }),
        ('Message Content', {
            'fields': ('subject', 'message')
        }),
        ('Email Status', {
            'fields': ('email_sent', 'email_failed', 'failure_reason', 'sent_at')
        }),
        ('Read Status', {
            'fields': ('is_read', 'read_at')
        }),
        ('Related Objects', {
            'fields': ('related_grade', 'related_fee', 'related_enrollment'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'isbn', 'category', 'total_copies', 'available_copies')
    search_fields = ('title', 'author', 'isbn')
    list_filter = ('category',)

@admin.register(BookInstance)
class BookInstanceAdmin(admin.ModelAdmin):
    list_display = ('book', 'book_id_number', 'status', 'added_at')
    search_fields = ('book__title', 'book_id_number')
    list_filter = ('status',)

@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ('book_instance', 'user', 'borrow_date', 'due_date', 'status', 'fine_amount')
    search_fields = ('user__username', 'book_instance__book_id_number', 'book_instance__book__title')
    list_filter = ('status', 'borrow_date', 'due_date')

@admin.register(Classroom)
class ClassroomAdmin(admin.ModelAdmin):
    list_display = ('building', 'room_number', 'capacity', 'has_projector')
    search_fields = ('building', 'room_number')

@admin.register(TimetableSlot)
class TimetableSlotAdmin(admin.ModelAdmin):
    list_display = ('course', 'day_of_week', 'start_time', 'end_time', 'classroom')
    list_filter = ('day_of_week', 'classroom')
    search_fields = ('course__code', 'course__name')

@admin.register(Exam)
class ExamAdmin(admin.ModelAdmin):
    list_display = ('course', 'exam_type', 'date', 'start_time', 'end_time', 'classroom')
    list_filter = ('exam_type', 'date')
    search_fields = ('course__code', 'course__name')

from .models import LeaveRequest

@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'status', 'applied_on')
    list_filter = ('status', 'start_date', 'applied_on')
    search_fields = ('user__username', 'user__first_name', 'reason')
