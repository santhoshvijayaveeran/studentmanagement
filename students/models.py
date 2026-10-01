from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone


class User(AbstractUser):
    """Custom User model with role-based access control."""
    
    ROLE_CHOICES = (
        ('admin', 'Administrator'),
        ('faculty', 'Faculty/Instructor'),
        ('student', 'Student'),
    )
    
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='student')
    phone = models.CharField(max_length=20, blank=True, null=True)
    department = models.CharField(max_length=100, blank=True, null=True)
    enrollment_year = models.IntegerField(blank=True, null=True)
    
    class Meta:
        ordering = ['-date_joined']
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_role_display()})"
    
    def is_admin(self):
        return self.role == 'admin'
    
    def is_faculty(self):
        return self.role == 'faculty'
    
    def is_student(self):
        return self.role == 'student'


class Faculty(models.Model):
    """Faculty/Instructor model."""
    
    DEPARTMENT_CHOICES = (
        ('cse', 'Computer Science & Engineering'),
        ('ece', 'Electronics & Communication'),
        ('me', 'Mechanical Engineering'),
        ('ce', 'Civil Engineering'),
        ('eee', 'Electrical & Electronics'),
        ('it', 'Information Technology'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='faculty_profile')
    employee_id = models.CharField(max_length=60, unique=True)
    department = models.CharField(max_length=20, choices=DEPARTMENT_CHOICES)
    specialization = models.CharField(max_length=200, blank=True)
    experience_years = models.IntegerField(default=0)
    office_location = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Faculty"
    
    def __str__(self):
        return f"{self.user.get_full_name()} ({self.employee_id})"


class Student(models.Model):
    """Student model."""
    
    DEPARTMENT_CHOICES = (
        ('cse', 'Computer Science & Engineering'),
        ('ece', 'Electronics & Communication'),
        ('me', 'Mechanical Engineering'),
        ('ce', 'Civil Engineering'),
        ('eee', 'Electrical & Electronics'),
        ('it', 'Information Technology'),
    )
    
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile', blank=True, null=True)
    name = models.CharField(max_length=120)
    roll_number = models.CharField(max_length=60, unique=True)
    email = models.EmailField(max_length=254)
    phone = models.CharField(max_length=20)
    department = models.CharField(max_length=100, choices=DEPARTMENT_CHOICES)
    date_of_birth = models.DateField()
    enrollment_year = models.IntegerField(blank=True, null=True, default=2024)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} ({self.roll_number})"


class Department(models.Model):
    """Academic Department model."""
    
    DEPT_CHOICES = (
        ('cse', 'Computer Science & Engineering'),
        ('ece', 'Electronics & Communication'),
        ('me', 'Mechanical Engineering'),
        ('ce', 'Civil Engineering'),
        ('eee', 'Electrical & Electronics'),
        ('it', 'Information Technology'),
    )
    
    code = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    hod = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments')
    total_seats = models.IntegerField(default=100)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['name']
        verbose_name_plural = "Departments"
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class Course(models.Model):
    """Course model."""
    
    SEMESTER_CHOICES = [
        (1, '1st Semester'),
        (2, '2nd Semester'),
        (3, '3rd Semester'),
        (4, '4th Semester'),
        (5, '5th Semester'),
        (6, '6th Semester'),
        (7, '7th Semester'),
        (8, '8th Semester'),
    ]
    
    code = models.CharField(max_length=20, unique=True)
    name = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    department = models.ForeignKey(Department, on_delete=models.CASCADE, related_name='courses')
    instructor = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, blank=True, related_name='courses_taught')
    semester = models.IntegerField(choices=SEMESTER_CHOICES)
    credits = models.IntegerField(default=3)
    capacity = models.IntegerField(default=60)
    room = models.CharField(max_length=50, blank=True)
    schedule = models.CharField(max_length=200, blank=True)  # e.g., "MWF 10:00-11:00"
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['department', 'code']
        unique_together = ('code', 'semester')
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class Enrollment(models.Model):
    """Course Enrollment model."""
    
    STATUS_CHOICES = [
        ('enrolled', 'Enrolled'),
        ('completed', 'Completed'),
        ('dropped', 'Dropped'),
        ('pending', 'Pending'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    enrollment_date = models.DateTimeField(auto_now_add=True)
    semester_year = models.IntegerField()  # e.g., 2024

    class Meta:
        unique_together = ('student', 'course')
        ordering = ['-enrollment_date']

    def __str__(self):
        return f"{self.student.name} - {self.course.code}"

    @property
    def semester(self):
        """Expose the semester from the related course."""
        return self.course.semester if self.course else None


class Attendance(models.Model):
    """Attendance tracking model."""
    
    ATTENDANCE_CHOICES = [
        ('present', 'Present'),
        ('absent', 'Absent'),
        ('late', 'Late'),
        ('excused', 'Excused'),
    ]
    
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='attendances')
    date = models.DateField()
    status = models.CharField(max_length=20, choices=ATTENDANCE_CHOICES, default='present')
    remarks = models.CharField(max_length=200, blank=True)
    recorded_by = models.ForeignKey(Faculty, on_delete=models.SET_NULL, null=True, related_name='attendances_recorded')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('enrollment', 'date')
        ordering = ['-date']
        verbose_name_plural = "Attendance"
    
    def __str__(self):
        return f"{self.enrollment.student.name} - {self.date} ({self.status})"


class Grade(models.Model):
    """Grade/Mark model."""

    def __init__(self, *args, **kwargs):
        marks = kwargs.pop('marks', None)
        super().__init__(*args, **kwargs)
        if marks is not None:
            clamped = max(0, min(marks, 100))
            self.internal_marks = min(clamped, 40)
            remaining = clamped - self.internal_marks
            self.external_marks = min(max(remaining, 0), 60)
    
    GRADE_CHOICES = [
        ('A+', 'A+ (90-100)'),
        ('A', 'A (80-89)'),
        ('B+', 'B+ (70-79)'),
        ('B', 'B (60-69)'),
        ('C', 'C (50-59)'),
        ('D', 'D (40-49)'),
        ('F', 'F (Below 40)'),
    ]
    
    enrollment = models.OneToOneField(Enrollment, on_delete=models.CASCADE, related_name='grade')
    internal_marks = models.IntegerField(default=0, help_text="Out of 40")
    external_marks = models.IntegerField(default=0, help_text="Out of 60")
    total_marks = models.IntegerField(default=0, editable=False)
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    grade = models.CharField(max_length=3, choices=GRADE_CHOICES, blank=True)
    remarks = models.CharField(max_length=200, blank=True)
    released = models.BooleanField(default=False)
    released_date = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-released_date']
    
    def save(self, *args, **kwargs):
        self.total_marks = self.internal_marks + self.external_marks
        self.percentage = (self.total_marks / 100) * 100
        
        # Auto-assign grade based on percentage
        if self.percentage >= 90:
            self.grade = 'A+'
        elif self.percentage >= 80:
            self.grade = 'A'
        elif self.percentage >= 70:
            self.grade = 'B+'
        elif self.percentage >= 60:
            self.grade = 'B'
        elif self.percentage >= 50:
            self.grade = 'C'
        elif self.percentage >= 40:
            self.grade = 'D'
        else:
            self.grade = 'F'
        
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.enrollment.student.name} - {self.enrollment.course.code}: {self.grade}"

    @property
    def marks(self):
        """Total marks out of 100 (internal + external)."""
        return self.internal_marks + self.external_marks

    def get_percentage(self):
        """Return the stored percentage value."""
        try:
            return float(self.percentage)
        except (TypeError, ValueError):
            return 0.0


class Fee(models.Model):
    """Fee/Payment model."""
    
    FEE_TYPE_CHOICES = [
        ('tuition', 'Tuition Fee'),
        ('hostel', 'Hostel Fee'),
        ('exam', 'Exam Fee'),
        ('library', 'Library Fee'),
        ('activity', 'Activity Fee'),
        ('misc', 'Miscellaneous'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pending'),
        ('partial', 'Partial Paid'),
        ('paid', 'Fully Paid'),
    ]
    
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees')
    fee_type = models.CharField(max_length=20, choices=FEE_TYPE_CHOICES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    due_date = models.DateField()
    paid_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    payment_date = models.DateField(null=True, blank=True)
    remarks = models.CharField(max_length=200, blank=True)
    semester = models.IntegerField()
    year = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-due_date']
        unique_together = ('student', 'fee_type', 'semester', 'year')
    
    def __str__(self):
        return f"{self.student.name} - {self.get_fee_type_display()} - {self.payment_status}"
    
    @property
    def outstanding_amount(self):
        return self.amount - self.paid_amount


class Transcript(models.Model):
    """Academic Transcript model - Computed GPA and cumulative performance."""
    
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='transcript')
    cumulative_gpa = models.DecimalField(max_digits=4, decimal_places=2, default=0, editable=False)
    total_credits_completed = models.IntegerField(default=0, editable=False)
    total_credits_attempted = models.IntegerField(default=0, editable=False)
    total_courses_passed = models.IntegerField(default=0, editable=False)
    total_courses_failed = models.IntegerField(default=0, editable=False)
    cumulative_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    academic_standing = models.CharField(max_length=50, default='Good', choices=[
        ('Excellent', 'Excellent (GPA >= 3.7)'),
        ('Very Good', 'Very Good (GPA 3.4-3.69)'),
        ('Good', 'Good (GPA 3.0-3.39)'),
        ('Satisfactory', 'Satisfactory (GPA 2.0-2.99)'),
        ('Probation', 'Probation (GPA < 2.0)'),
    ])
    last_updated = models.DateTimeField(auto_now=True)
    generated_date = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Transcripts"
        ordering = ['-generated_date']
    
    def __str__(self):
        return f"{self.student.name} - Transcript (GPA: {self.cumulative_gpa})"
    
    def calculate_gpa(self):
        """Calculate cumulative GPA based on released grades with credits."""
        from decimal import Decimal
        
        grades = self.student.enrollments.filter(
            grade__released=True,
            course__isnull=False
        ).select_related('course', 'grade')
        
        if not grades.exists():
            return 0
        
        total_grade_points = Decimal('0')
        total_credits = 0
        courses_passed = 0
        courses_failed = 0
        
        for enrollment in grades:
            grade = enrollment.grade
            credits = enrollment.course.credits
            
            # GPA mapping: A+=4.0, A=4.0, B+=3.5, B=3.0, C=2.5, D=2.0, F=0
            grade_point_map = {
                'A+': 4.0, 'A': 4.0, 'B+': 3.5, 'B': 3.0,
                'C': 2.5, 'D': 2.0, 'F': 0
            }
            
            grade_points = grade_point_map.get(grade.grade, 0)
            total_grade_points += Decimal(grade_points * credits)
            total_credits += credits
            
            if grade.grade != 'F':
                courses_passed += 1
            else:
                courses_failed += 1
        
        gpa = total_grade_points / total_credits if total_credits > 0 else 0
        return round(float(gpa), 2)
    
    def update_transcript(self):
        """Recalculate transcript statistics."""
        grades = self.student.enrollments.filter(grade__released=True).select_related('grade', 'course')
        
        if grades.exists():
            self.cumulative_gpa = self.calculate_gpa()
            self.total_credits_completed = sum(
                e.course.credits for e in grades 
                if e.grade.grade != 'F'
            )
            self.total_credits_attempted = sum(e.course.credits for e in grades)
            self.total_courses_passed = grades.filter(grade__grade__in=['A+', 'A', 'B+', 'B', 'C', 'D']).count()
            self.total_courses_failed = grades.filter(grade__grade='F').count()
            
            # Calculate cumulative percentage
            all_grades = grades.values_list('grade__percentage', flat=True)
            if all_grades:
                self.cumulative_percentage = sum(all_grades) / len(all_grades)
            
            # Set academic standing
            if self.cumulative_gpa >= 3.7:
                self.academic_standing = 'Excellent'
            elif self.cumulative_gpa >= 3.4:
                self.academic_standing = 'Very Good'
            elif self.cumulative_gpa >= 3.0:
                self.academic_standing = 'Good'
            elif self.cumulative_gpa >= 2.0:
                self.academic_standing = 'Satisfactory'
            else:
                self.academic_standing = 'Probation'
            
            self.save()


class DegreeAudit(models.Model):
    """Degree requirement tracking model."""
    
    STATUS_CHOICES = [
        ('completed', 'Completed'),
        ('in_progress', 'In Progress'),
        ('not_started', 'Not Started'),
    ]
    
    student = models.OneToOneField(Student, on_delete=models.CASCADE, related_name='degree_audit')
    degree_name = models.CharField(max_length=100, default='Bachelor of Technology')
    total_credits_required = models.IntegerField(default=120)
    core_courses_required = models.IntegerField(default=30)
    elective_courses_required = models.IntegerField(default=20)
    
    core_courses_completed = models.IntegerField(default=0, editable=False)
    elective_courses_completed = models.IntegerField(default=0, editable=False)
    total_credits_earned = models.IntegerField(default=0, editable=False)
    
    overall_progress = models.IntegerField(default=0, editable=False, help_text="Progress percentage")
    expected_graduation = models.DateField(null=True, blank=True)
    audit_status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='in_progress')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Degree Audits"
    
    def __str__(self):
        return f"{self.student.name} - {self.degree_name}"
    
    def update_progress(self):
        """Calculate degree completion progress."""
        passed_enrollments = self.student.enrollments.filter(
            grade__released=True,
            grade__grade__in=['A+', 'A', 'B+', 'B', 'C', 'D']
        ).select_related('course')
        
        self.total_credits_earned = sum(e.course.credits for e in passed_enrollments)
        self.overall_progress = int((self.total_credits_earned / self.total_credits_required) * 100)
        
        if self.overall_progress >= 100:
            self.audit_status = 'completed'
        elif self.overall_progress > 0:
            self.audit_status = 'in_progress'
        
        self.save()


class FacultyReport(models.Model):
    """Faculty performance and analytics report model."""
    
    faculty = models.OneToOneField(Faculty, on_delete=models.CASCADE, related_name='performance_report')
    
    # Course Statistics
    total_courses_taught = models.IntegerField(default=0, editable=False)
    current_semester_courses = models.IntegerField(default=0, editable=False)
    total_students_taught = models.IntegerField(default=0, editable=False)
    current_semester_students = models.IntegerField(default=0, editable=False)
    
    # Grade Statistics
    average_class_gpa = models.DecimalField(max_digits=4, decimal_places=2, default=0, editable=False)
    average_grades_given = models.CharField(max_length=2, default='B', editable=False, help_text="Average letter grade")
    
    # Performance Metrics
    student_satisfaction_score = models.DecimalField(max_digits=3, decimal_places=2, default=0, null=True, blank=True)
    pass_rate_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    fail_rate_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0, editable=False)
    
    # Grade Distribution
    grade_a_count = models.IntegerField(default=0, editable=False)  # A+/A combined
    grade_b_count = models.IntegerField(default=0, editable=False)  # B+/B combined
    grade_c_count = models.IntegerField(default=0, editable=False)
    grade_d_count = models.IntegerField(default=0, editable=False)
    grade_f_count = models.IntegerField(default=0, editable=False)
    
    # Workload Analysis
    total_credits_assigned = models.IntegerField(default=0, editable=False)
    average_class_size = models.IntegerField(default=0, editable=False)
    peak_semester_load = models.IntegerField(default=0, editable=False, help_text="Maximum credits in one semester")
    
    # Dates
    generated_date = models.DateTimeField(auto_now_add=True)
    last_updated = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = "Faculty Reports"
        ordering = ['-last_updated']
    
    def __str__(self):
        return f"{self.faculty.user.get_full_name()} - Performance Report"
    
    def calculate_course_statistics(self):
        """Calculate course teaching statistics."""
        courses = self.faculty.courses_taught.all()
        enrollments = Enrollment.objects.filter(course__instructor=self.faculty)
        current_enrollments = enrollments.filter(status='enrolled')
        
        self.total_courses_taught = courses.count()
        self.current_semester_courses = courses.filter(semester__gt=0).count()
        self.total_students_taught = enrollments.values('student').distinct().count()
        self.current_semester_students = current_enrollments.count()
    
    def calculate_grade_statistics(self):
        """Calculate grade distribution and GPA statistics."""
        grades = Grade.objects.filter(enrollment__course__instructor=self.faculty, released=True)
        
        if grades.exists():
            # Calculate average GPA
            grade_point_map = {'A+': 4.0, 'A': 4.0, 'B+': 3.5, 'B': 3.0, 'C': 2.5, 'D': 2.0, 'F': 0}
            total_points = sum(grade_point_map.get(g.grade, 0) for g in grades)
            self.average_class_gpa = total_points / grades.count() if grades.count() > 0 else 0
            
            # Count grades
            self.grade_a_count = grades.filter(grade__in=['A+', 'A']).count()
            self.grade_b_count = grades.filter(grade__in=['B+', 'B']).count()
            self.grade_c_count = grades.filter(grade='C').count()
            self.grade_d_count = grades.filter(grade='D').count()
            self.grade_f_count = grades.filter(grade='F').count()
            
            total_grades = grades.count()
            self.pass_rate_percentage = ((total_grades - self.grade_f_count) / total_grades * 100) if total_grades > 0 else 0
            self.fail_rate_percentage = (self.grade_f_count / total_grades * 100) if total_grades > 0 else 0
            
            # Determine average grade
            if self.average_class_gpa >= 3.5:
                self.average_grades_given = 'A'
            elif self.average_class_gpa >= 3.0:
                self.average_grades_given = 'B'
            elif self.average_class_gpa >= 2.5:
                self.average_grades_given = 'C'
            else:
                self.average_grades_given = 'D'
    
    def calculate_workload_statistics(self):
        """Calculate instructor workload analysis."""
        courses = self.faculty.courses_taught.all()
        enrollments = Enrollment.objects.filter(course__instructor=self.faculty, status='enrolled')
        
        # Total credits assigned
        self.total_credits_assigned = sum(c.credits for c in courses)
        
        # Average class size
        if courses.exists():
            total_students = enrollments.count()
            self.average_class_size = total_students // courses.count() if courses.count() > 0 else 0
        
        # Peak semester load
        if courses.exists():
            semester_loads = {}
            for course in courses:
                sem = course.semester
                semester_loads[sem] = semester_loads.get(sem, 0) + course.credits
            self.peak_semester_load = max(semester_loads.values()) if semester_loads else 0
    
    def update_report(self):
        """Recalculate all statistics."""
        self.calculate_course_statistics()
        self.calculate_grade_statistics()
        self.calculate_workload_statistics()
        self.save()


class Notification(models.Model):
    """Email Notification tracking model."""
    
    NOTIFICATION_TYPES = [
        ('grade_released', 'Grade Released'),
        ('fee_due', 'Fee Due Soon'),
        ('fee_overdue', 'Fee Overdue'),
        ('enrollment_confirmed', 'Enrollment Confirmed'),
        ('enrollment_rejected', 'Enrollment Rejected'),
        ('attendance_warning', 'Attendance Warning'),
        ('academic_warning', 'Academic Warning'),
        ('transcript_available', 'Transcript Available'),
        ('report_generated', 'Report Generated'),
        ('system_notification', 'System Notification'),
    ]
    
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    notification_type = models.CharField(max_length=50, choices=NOTIFICATION_TYPES)
    subject = models.CharField(max_length=255)
    message = models.TextField()
    email_sent = models.BooleanField(default=False)
    email_failed = models.BooleanField(default=False)
    failure_reason = models.TextField(blank=True, null=True)
    is_read = models.BooleanField(default=False)
    
    # Optional: track related objects
    related_grade = models.ForeignKey(Grade, on_delete=models.SET_NULL, blank=True, null=True)
    related_fee = models.ForeignKey(Fee, on_delete=models.SET_NULL, blank=True, null=True)
    related_enrollment = models.ForeignKey(Enrollment, on_delete=models.SET_NULL, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(blank=True, null=True)
    read_at = models.DateTimeField(blank=True, null=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name_plural = "Notifications"
    
    def __str__(self):
        return f"{self.get_notification_type_display()} - {self.recipient.username}"
    
    def mark_as_read(self):
        """Mark notification as read."""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save()
    
    def mark_as_sent(self):
        """Mark notification as successfully sent."""
        if not self.email_sent:
            self.email_sent = True
            self.sent_at = timezone.now()
            self.email_failed = False
            self.failure_reason = None
            self.save()
    
    def mark_as_failed(self, reason):
        """Mark notification as failed to send."""
        self.email_failed = True
        self.failure_reason = reason
        self.save()

# ==================== LIBRARY MANAGEMENT MODELS ====================

class Book(models.Model):
    """Catalog holding general information about a specific book title."""
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    isbn = models.CharField(max_length=17, unique=True, verbose_name="ISBN")
    category = models.CharField(max_length=100)
    publisher = models.CharField(max_length=255, blank=True, null=True)
    publication_year = models.IntegerField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title} by {self.author}"
    
    @property
    def total_copies(self):
        return self.instances.count()
        
    @property
    def available_copies(self):
        return self.instances.filter(status='available').count()

class BookInstance(models.Model):
    """A specific physical copy of a book."""
    STATUS_CHOICES = (
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('lost', 'Lost'),
        ('maintenance', 'Maintenance'),
    )
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='instances')
    book_id_number = models.CharField(max_length=50, unique=True, help_text="Unique ID for this physical book")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    added_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.book.title} ({self.book_id_number})"

class BorrowRecord(models.Model):
    """Record of a book being borrowed by a user (student/faculty)."""
    STATUS_CHOICES = (
        ('active', 'Active'),
        ('returned', 'Returned'),
        ('overdue', 'Overdue'),
    )
    book_instance = models.ForeignKey(BookInstance, on_delete=models.CASCADE, related_name='borrow_records')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='borrow_records')
    borrow_date = models.DateField(default=timezone.now)
    due_date = models.DateField()
    return_date = models.DateField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    fine_amount = models.DecimalField(max_digits=6, decimal_places=2, default=0.00)
    
    def __str__(self):
        return f"{self.user.username} borrowed {self.book_instance}"
    
    def calculate_fine(self):
        """Calculate fine based on $1/day overdue."""
        if self.status == 'returned' and self.return_date:
            days_overdue = (self.return_date - self.due_date).days
        elif self.status in ['active', 'overdue']:
            days_overdue = (timezone.now().date() - self.due_date).days
        else:
            days_overdue = 0
            
        if days_overdue > 0:
            self.fine_amount = days_overdue * 1.00  # $1 per day
            if self.status == 'active':
                self.status = 'overdue'
            self.save()
        return self.fine_amount

# ==================== SCHEDULE & EXAM MODELS ====================

class Classroom(models.Model):
    """Physical location for a class or exam."""
    room_number = models.CharField(max_length=50, unique=True)
    building = models.CharField(max_length=100)
    capacity = models.IntegerField()
    has_projector = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.building} - {self.room_number}"

class TimetableSlot(models.Model):
    """A specific time slot for a course."""
    DAY_CHOICES = (
        ('MON', 'Monday'), ('TUE', 'Tuesday'), ('WED', 'Wednesday'),
        ('THU', 'Thursday'), ('FRI', 'Friday'), ('SAT', 'Saturday')
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='timetable_slots')
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True)
    day_of_week = models.CharField(max_length=3, choices=DAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    
    class Meta:
        ordering = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.course.code} on {self.get_day_of_week_display()} ({self.start_time.strftime('%H:%M')} - {self.end_time.strftime('%H:%M')})"

class Exam(models.Model):
    """Formal examination for a specific course."""
    TITLE_CHOICES = (
        ('midterm', 'Midterm Examination'),
        ('final', 'Final Examination'),
        ('quiz', 'Pop Quiz / Assessment'),
    )
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='exams')
    exam_type = models.CharField(max_length=20, choices=TITLE_CHOICES)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    classroom = models.ForeignKey(Classroom, on_delete=models.SET_NULL, null=True, blank=True)
    total_marks = models.IntegerField(default=100)
    
    class Meta:
        ordering = ['date', 'start_time']
        
    def __str__(self):
        return f"{self.get_exam_type_display()} - {self.course.code} ({self.date})"

# ==================== LEAVE MANAGEMENT MODELS ====================

class LeaveRequest(models.Model):
    """Request for leave submitted by a student or faculty."""
    STATUS_CHOICES = (
        ('pending', 'Pending Approval'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_on = models.DateTimeField(auto_now_add=True)
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='reviewed_leaves')
    rejection_reason = models.TextField(blank=True, null=True)
    
    class Meta:
        ordering = ['-applied_on']
        
    def __str__(self):
        return f"{self.user.username} - {self.start_date} to {self.end_date} ({self.status})"
    
    @property
    def duration_days(self):
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days + 1
        return 0
