from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Q
from django.core.paginator import Paginator
from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.http import HttpResponseForbidden, HttpResponse
from django.utils import timezone
from functools import wraps

from .models import Student, User, Faculty, Department, Course, Enrollment, Attendance, Grade, Fee, Transcript, DegreeAudit, FacultyReport, Notification, Book, BookInstance, BorrowRecord, Classroom, TimetableSlot, Exam, LeaveRequest
from .pdf_generator import generate_transcript_pdf, generate_faculty_report_pdf
from .forms import (
    StudentForm, UserLoginForm, UserSignupForm, FacultyForm,
    DepartmentForm, CourseForm, EnrollmentForm, AttendanceForm, GradeForm, FeeForm, TranscriptForm, DegreeAuditForm
)


# ==================== AUTHENTICATION VIEWS ====================

def user_login(request):
    """
    User login view.
    Handles POST requests with username and password.
    Redirects based on user role (student/faculty/admin).
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    form = UserLoginForm(request.POST or None)
    if form.is_valid():
        user = form.get_user()
        login(request, user)
        messages.success(request, f'Welcome back, {user.get_full_name() or user.username}!')
        
        # Redirect based on role
        if user.is_staff or user.is_superuser:
            return redirect('admin_dashboard')
        elif user.is_faculty():
            return redirect('faculty_dashboard')
        else:
            return redirect('student_portal')
    
    return render(request, 'students/login.html', {'form': form})


@require_http_methods(["GET", "POST"])
@login_required(login_url='login')
def user_logout(request):
    """
    Log the authenticated user out and redirect them back to the login page.
    Accepts both GET and POST so navigation links and direct browser requests work.
    """
    logout(request)
    messages.success(request, 'You have been logged out successfully.')
    return redirect('login')


def user_signup(request):
    """
    User registration/signup view.
    Allows new users to register as student or faculty.
    Creates Student or Faculty profile based on role.
    """
    if request.user.is_authenticated:
        return redirect('dashboard')
    
    form = UserSignupForm(request.POST or None)
    if form.is_valid():
        user = form.save()
        login(request, user)
        messages.success(request, f'Account created successfully! Welcome, {user.get_full_name()}!')
        
        # Create Student or Faculty profile
        role = form.cleaned_data.get('role', 'student')
        if role == 'student':
            Student.objects.create(
                user=user,
                name=f"{user.first_name} {user.last_name}",
                roll_number=f"STU{user.id}",
                email=user.email,
                phone=form.cleaned_data.get('phone', ''),
                department=form.cleaned_data.get('department', 'cse'),
                date_of_birth='2000-01-01',  # Placeholder to satisfy NOT NULL constraint
                enrollment_year=2024
            )
            return redirect('student_portal')
        else:
            # Faculty signup - redirect to complete faculty profile
            return redirect('faculty_profile_setup')
    
    return render(request, 'students/register.html', {'form': form})


# ==================== ROLE-BASED ACCESS DECORATORS ====================

def admin_only(func):
    """Decorator to restrict view access to admin users only."""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not (request.user.is_staff or request.user.is_superuser):
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('login')
        return func(request, *args, **kwargs)
    return wrapper


def faculty_only(func):
    """Decorator to restrict view access to faculty users only."""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_faculty():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('login')
        return func(request, *args, **kwargs)
    return wrapper


def student_only(func):
    """Decorator to restrict view access to student users only."""
    @wraps(func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_authenticated or not request.user.is_student():
            messages.error(request, 'You do not have permission to access this page.')
            return redirect('login')
        return func(request, *args, **kwargs)
    return wrapper


# ==================== DASHBOARD VIEWS ====================

@login_required(login_url='login')
def dashboard(request):
    """
    Universal dashboard that redirects to role-specific dashboard.
    """
    if request.user.is_staff or request.user.is_superuser:
        return redirect('admin_dashboard')
    elif request.user.is_faculty():
        return redirect('faculty_dashboard')
    else:
        return redirect('student_portal')


@admin_only
def admin_dashboard(request):
    """
    Admin dashboard with phase 2 statistics and operational data.
    """
    # Count statistics
    total_students = Student.objects.count()
    total_faculty = Faculty.objects.count()
    total_users = User.objects.count()
    
    # Phase 2 statistics
    total_departments = Department.objects.count()
    total_courses = Course.objects.count()
    total_enrollments = Enrollment.objects.count()
    total_fees = Fee.objects.count()
    
    # Fee analytics
    total_fee_amount = sum(f.amount for f in Fee.objects.all())
    paid_fees = Fee.objects.filter(payment_status='paid').count()
    pending_fees = Fee.objects.filter(payment_status='pending').count()
    
    # Recent data for dashboard cards
    recent_enrollments = Enrollment.objects.select_related('student', 'course').order_by('-enrollment_date')[:5]
    recent_grades = Grade.objects.select_related('enrollment__student', 'enrollment__course').filter(released=True).order_by('-released_date')[:5]
    recent_fees = Fee.objects.select_related('student').order_by('-created_at')[:5]
    
    context = {
        # Basic stats
        'total_students': total_students,
        'total_faculty': total_faculty,
        'total_users': total_users,
        
        # Phase 2 stats
        'total_departments': total_departments,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'total_fees': total_fees,
        'total_fee_amount': total_fee_amount,
        'paid_fees': paid_fees,
        'pending_fees': pending_fees,
        
        # Recent data
        'recent_enrollments': recent_enrollments,
        'recent_grades': recent_grades,
        'recent_fees': recent_fees,
    }
    return render(request, 'students/admin_dashboard.html', context)


@faculty_only
def faculty_dashboard(request):
    """
    Faculty dashboard with instructor-specific data and analytics.
    """
    try:
        faculty = request.user.faculty_profile
    except Faculty.DoesNotExist:
        faculty = None
    
    # Faculty's courses
    courses = Course.objects.filter(instructor=faculty) if faculty else []
    total_courses = courses.count()
    
    # Enrollments in faculty's courses
    course_ids = courses.values_list('id', flat=True)
    total_enrollments = Enrollment.objects.filter(course_id__in=course_ids).count()
    recent_enrollments = Enrollment.objects.filter(course_id__in=course_ids).select_related('student', 'course').order_by('-enrollment_date')[:5]
    
    # Grades given by faculty (for recent grades)
    recent_grades = Grade.objects.filter(enrollment__course_id__in=course_ids).select_related(
        'enrollment__student', 'enrollment__course'
    ).filter(released=True).order_by('-released_date')[:5]
    
    # Attendance records for faculty's courses
    attendance_records = Attendance.objects.filter(
        enrollment__course_id__in=course_ids,
        recorded_by=faculty
    ).count()
    
    # Average performance in faculty's courses
    grades_in_courses = Grade.objects.filter(enrollment__course_id__in=course_ids)
    avg_percentage = sum(g.percentage for g in grades_in_courses) / grades_in_courses.count() if grades_in_courses.count() > 0 else 0
    
    context = {
        'faculty': faculty,
        'total_courses': total_courses,
        'total_enrollments': total_enrollments,
        'attendance_records': attendance_records,
        'avg_percentage': round(avg_percentage, 2),
        'recent_enrollments': recent_enrollments,
        'recent_grades': recent_grades,
        'courses': courses[:5],  # Show latest 5 courses
    }
    return render(request, 'students/faculty_dashboard.html', context)


@login_required(login_url='login')
def student_portal(request):
    """
    Student portal/dashboard with enrollment, grades, and fee information.
    """
    try:
        student = request.user.student_profile
    except Student.DoesNotExist:
        student = None
    
    # Student's enrollments
    if student:
        enrollments = Enrollment.objects.filter(student=student).select_related('course__instructor', 'course__department')
        total_enrollments = enrollments.count()
        active_enrollments = enrollments.filter(status='enrolled').count()
    else:
        enrollments = []
        total_enrollments = 0
        active_enrollments = 0
    
    # Student's grades
    grades = Grade.objects.filter(enrollment__student=student, released=True).select_related(
        'enrollment__course'
    ).order_by('-released_date') if student else []
    
    # Student's fees
    if student:
        fees = Fee.objects.filter(student=student).order_by('-created_at')
        total_fees = sum(f.amount for f in fees)
        total_paid = sum(f.paid_amount for f in fees)
        pending_fee_count = fees.filter(payment_status='pending').count()
        paid_fee_count = fees.filter(payment_status='paid').count()
    else:
        fees = []
        total_fees = 0
        total_paid = 0
        pending_fee_count = 0
        paid_fee_count = 0
        
    outstanding_fees = total_fees - total_paid
    
    # Calculate average grade percentage
    avg_percentage = sum(g.percentage for g in grades) / len(grades) if len(grades) > 0 else 0
    
    # Attendance percentage (calculate based on attendance records)
    if student and enrollments:
        enrollment_ids = enrollments.values_list('id', flat=True)
        attendance_records = Attendance.objects.filter(enrollment_id__in=enrollment_ids)
        total_attendance = attendance_records.count()
        present_count = attendance_records.filter(status='present').count()
        attendance_percentage = (present_count / total_attendance * 100) if total_attendance > 0 else 0
    else:
        attendance_percentage = 0
    
    context = {
        'student': student,
        'total_enrollments': total_enrollments,
        'active_enrollments': active_enrollments,
        'enrollments': enrollments[:6],  # Show latest 6 enrollments
        'grades': grades[:6],  # Show latest 6 grades
        'avg_percentage': round(avg_percentage, 2),
        'attendance_percentage': round(attendance_percentage, 2),
        'total_fees': total_fees,
        'total_paid': total_paid,
        'outstanding_fees': outstanding_fees,
        'pending_fee_count': pending_fee_count,
        'paid_fee_count': paid_fee_count,
        'fees': fees[:5],  # Show latest 5 fees
    }
    return render(request, 'students/student_portal.html', context)


def faculty_profile_setup(request):
    """
    Setup faculty profile after registration.
    """
    if not request.user.is_authenticated or not request.user.is_faculty():
        return redirect('login')
    
    try:
        faculty = request.user.faculty_profile
        return redirect('faculty_dashboard')
    except Faculty.DoesNotExist:
        pass
    
    form = FacultyForm(request.POST or None)
    if form.is_valid():
        faculty = form.save(commit=False)
        faculty.user = request.user
        faculty.save()
        messages.success(request, 'Faculty profile created successfully!')
        return redirect('faculty_dashboard')
    
    return render(request, 'students/faculty_profile_setup.html', {'form': form})


# ==================== STUDENT MANAGEMENT VIEWS ====================

@login_required(login_url='login')
@admin_only
def student_list(request):
    """
    Display a paginated list of all students.
    Supports searching by name or roll number via 'q' query parameter.
    Admin only.
    """
    q = request.GET.get('q', '')
    if q:
        students = Student.objects.filter(
            Q(name__icontains=q) | Q(roll_number__icontains=q)
        ).order_by('-created_at')
    else:
        students = Student.objects.all().order_by('-created_at')
    
    page = Paginator(students, 8).get_page(request.GET.get('page'))
    
    context = {
        'students': page,
        'query': q,
        'total_students': Student.objects.count(),
        'active_courses': Course.objects.filter(is_active=True).count() if hasattr(Course, 'is_active') else Course.objects.count(),
        'faculty_count': Faculty.objects.count(),
        'new_enrollments': Enrollment.objects.filter(status='enrolled').count() if hasattr(Enrollment, 'status') else Enrollment.objects.count(),
    }
    return render(request, 'students/student_list.html', context)


@login_required(login_url='login')
@admin_only
def student_create(request):
    """
    Create a new student record.
    Admin only.
    """
    form = StudentForm(request.POST or None)
    if form.is_valid():
        student = form.save()
        messages.success(request, 'Student added successfully!')
        return redirect('student_list')
    return render(request, 'students/student_form.html', {'form': form, 'title': 'Add Student'})


@login_required(login_url='login')
@admin_only
def student_update(request, student_id):
    """
    Update an existing student record.
    Admin only.
    """
    student = get_object_or_404(Student, pk=student_id)
    form = StudentForm(request.POST or None, instance=student)
    if form.is_valid():
        form.save()
        messages.success(request, 'Student updated successfully!')
        return redirect('student_list')
    return render(request, 'students/student_form.html', {'form': form, 'title': 'Edit Student', 'student': student})


@login_required(login_url='login')
@admin_only
def student_delete(request, student_id):
    """
    Delete a student record.
    Admin only.
    """
    student = get_object_or_404(Student, pk=student_id)
    if request.method == 'POST':
        student.delete()
        messages.success(request, 'Student deleted successfully!')
        return redirect('student_list')
    return render(request, 'students/student_confirm_delete.html', {'student': student})


# ==================== DEPARTMENT MANAGEMENT ====================

@login_required(login_url='login')
@admin_only
def department_list(request):
    """List all departments."""
    query = request.GET.get('q', '')
    if query:
        departments = Department.objects.filter(Q(code__icontains=query) | Q(name__icontains=query))
    else:
        departments = Department.objects.all()
    
    page = Paginator(departments.order_by('code'), 10).get_page(request.GET.get('page'))
    context = {'departments': page, 'query': query}
    return render(request, 'students/department_list.html', context)


@login_required(login_url='login')
@admin_only
def department_create(request):
    """Create a new department."""
    form = DepartmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Department created successfully!')
        return redirect('department_list')
    return render(request, 'students/department_form.html', {'form': form, 'title': 'Create Department'})


@login_required(login_url='login')
@admin_only
def department_update(request, dept_id):
    """Update a department."""
    department = get_object_or_404(Department, pk=dept_id)
    form = DepartmentForm(request.POST or None, instance=department)
    if form.is_valid():
        form.save()
        messages.success(request, 'Department updated successfully!')
        return redirect('department_list')
    return render(request, 'students/department_form.html', {'form': form, 'title': 'Edit Department', 'department': department})


@login_required(login_url='login')
@admin_only
def department_delete(request, dept_id):
    """Delete a department."""
    department = get_object_or_404(Department, pk=dept_id)
    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Department deleted successfully!')
        return redirect('department_list')
    return render(request, 'students/department_confirm_delete.html', {'department': department})


# ==================== COURSE MANAGEMENT ====================

@login_required(login_url='login')
def course_list(request):
    """List all courses with optional filtering."""
    courses = Course.objects.all()
    
    # Filter by department if specified
    dept = request.GET.get('dept')
    if dept:
        courses = courses.filter(department__code=dept)
    
    # Paginate
    page = Paginator(courses, 10).get_page(request.GET.get('page'))
    departments = Department.objects.all()
    
    context = {
        'courses': page,
        'departments': departments,
        'selected_dept': dept,
        'total_courses': Course.objects.count(),
    }
    return render(request, 'students/course_list.html', context)


@login_required(login_url='login')
@admin_only
def course_create(request):
    """Create a new course."""
    form = CourseForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Course created successfully!')
        return redirect('course_list')
    return render(request, 'students/course_form.html', {'form': form, 'title': 'Create Course'})


@login_required(login_url='login')
@admin_only
def course_update(request, course_id):
    """Update a course."""
    course = get_object_or_404(Course, pk=course_id)
    form = CourseForm(request.POST or None, instance=course)
    if form.is_valid():
        form.save()
        messages.success(request, 'Course updated successfully!')
        return redirect('course_list')
    return render(request, 'students/course_form.html', {'form': form, 'title': 'Edit Course', 'course': course})


@login_required(login_url='login')
@admin_only
def course_delete(request, course_id):
    """Delete a course."""
    course = get_object_or_404(Course, pk=course_id)
    if request.method == 'POST':
        course.delete()
        messages.success(request, 'Course deleted successfully!')
        return redirect('course_list')
    return render(request, 'students/course_confirm_delete.html', {'course': course})


# ==================== ENROLLMENT MANAGEMENT ====================

@login_required(login_url='login')
def enrollment_list(request):
    """List enrollments."""
    if request.user.is_admin():
        enrollments = Enrollment.objects.all()
    elif request.user.is_faculty():
        # Faculty can see enrollments for their courses
        enrollments = Enrollment.objects.filter(course__instructor=request.user.faculty_profile)
    else:
        # Students can see their own enrollments
        if hasattr(request.user, 'student_profile'):
            enrollments = Enrollment.objects.filter(student=request.user.student_profile)
        else:
            enrollments = Enrollment.objects.none()
    
    page = Paginator(enrollments, 15).get_page(request.GET.get('page'))
    context = {'enrollments': page}
    return render(request, 'students/enrollment_list.html', context)


@login_required(login_url='login')
@admin_only
def enrollment_create(request):
    """Create a new enrollment."""
    form = EnrollmentForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Enrollment created successfully!')
        return redirect('enrollment_list')
    return render(request, 'students/enrollment_form.html', {'form': form, 'title': 'Create Enrollment'})


@login_required(login_url='login')
@admin_only
def enrollment_update(request, enroll_id):
    """Update an enrollment."""
    enrollment = get_object_or_404(Enrollment, pk=enroll_id)
    form = EnrollmentForm(request.POST or None, instance=enrollment)
    if form.is_valid():
        form.save()
        messages.success(request, 'Enrollment updated successfully!')
        return redirect('enrollment_list')
    return render(request, 'students/enrollment_form.html', {'form': form, 'title': 'Edit Enrollment', 'enrollment': enrollment})


@login_required(login_url='login')
@admin_only
def enrollment_delete(request, enroll_id):
    """Delete an enrollment."""
    enrollment = get_object_or_404(Enrollment, pk=enroll_id)
    if request.method == 'POST':
        enrollment.delete()
        messages.success(request, 'Enrollment deleted successfully!')
        return redirect('enrollment_list')
    return render(request, 'students/enrollment_confirm_delete.html', {'enrollment': enrollment})


# ==================== ATTENDANCE MANAGEMENT ====================

@login_required(login_url='login')
def attendance_list(request):
    """List attendance records."""
    if request.user.is_admin():
        attendance = Attendance.objects.all()
    elif request.user.is_faculty():
        # Faculty can see attendance for their courses
        attendance = Attendance.objects.filter(enrollment__course__instructor=request.user.faculty_profile)
    else:
        # Students can see their own attendance
        if hasattr(request.user, 'student_profile'):
            attendance = Attendance.objects.filter(enrollment__student=request.user.student_profile)
        else:
            attendance = Attendance.objects.none()
    
    page = Paginator(attendance.order_by('-date'), 20).get_page(request.GET.get('page'))
    context = {'attendance': page}
    return render(request, 'students/attendance_list.html', context)


@login_required(login_url='login')
@faculty_only
def attendance_record(request):
    """Record attendance for a course."""
    form = AttendanceForm(request.POST or None)
    if form.is_valid():
        enrollment = form.cleaned_data['enrollment']
        if not request.user.is_admin() and enrollment.course.instructor != getattr(request.user, 'faculty_profile', None):
            return HttpResponseForbidden("You don't have permission to record attendance for this course.")
        form.save()
        messages.success(request, 'Attendance recorded successfully!')
        return redirect('attendance_list')
    return render(request, 'students/attendance_form.html', {'form': form, 'title': 'Record Attendance'})


@login_required(login_url='login')
@faculty_only
def attendance_update(request, record_id):
    """Update attendance record."""
    record = get_object_or_404(Attendance, id=record_id)

    # Faculty may only edit attendance for courses they teach
    if not request.user.is_admin() and record.enrollment.course.instructor != getattr(request.user, 'faculty_profile', None):
        return HttpResponseForbidden("You don't have permission to edit this attendance record.")

    form = AttendanceForm(request.POST or None, instance=record)
    if form.is_valid():
        form.save()
        messages.success(request, 'Attendance updated successfully!')
        return redirect('attendance_list')
    return render(request, 'students/attendance_form.html', {'form': form, 'title': 'Edit Attendance'})


# ==================== GRADE MANAGEMENT ====================

@login_required(login_url='login')
def grade_list(request):
    """List grades."""
    if request.user.is_admin():
        grades = Grade.objects.all()
    elif request.user.is_faculty():
        # Faculty can see grades for their courses
        if hasattr(request.user, 'faculty_profile'):
            grades = Grade.objects.filter(enrollment__course__instructor=request.user.faculty_profile)
        else:
            grades = Grade.objects.none()
    else:
        # Students can see their own grades
        if hasattr(request.user, 'student_profile'):
            grades = Grade.objects.filter(enrollment__student=request.user.student_profile)
        else:
            grades = Grade.objects.none()
    
    page = Paginator(grades.order_by('-released_date'), 15).get_page(request.GET.get('page'))
    context = {'grades': page}
    return render(request, 'students/grade_list.html', context)


@login_required(login_url='login')
@faculty_only
def grade_create(request, enroll_id):
    """Create a grade for an enrollment."""
    enrollment = get_object_or_404(Enrollment, pk=enroll_id)

    # Faculty may only grade enrollments in courses they teach
    if not request.user.is_admin() and enrollment.course.instructor != getattr(request.user, 'faculty_profile', None):
        return HttpResponseForbidden("You don't have permission to grade this enrollment.")

    # Check if grade already exists
    try:
        grade = Grade.objects.get(enrollment=enrollment)
        messages.info(request, 'Grade already exists for this enrollment.')
        return redirect('grade_list')
    except Grade.DoesNotExist:
        pass
    
    if request.method == 'POST':
        form = GradeForm(request.POST)
        if form.is_valid():
            grade = form.save(commit=False)
            grade.enrollment = enrollment
            grade.save()
            messages.success(request, 'Grade created successfully!')
            return redirect('grade_list')
    else:
        form = GradeForm()
    
    return render(request, 'students/grade_form.html', {'form': form, 'title': 'Create Grade', 'enrollment': enrollment})


@login_required(login_url='login')
@faculty_only
def grade_update(request, grade_id):
    """Update a grade."""
    grade = get_object_or_404(Grade, pk=grade_id)

    # Faculty may only edit grades in courses they teach
    if not request.user.is_admin() and grade.enrollment.course.instructor != getattr(request.user, 'faculty_profile', None):
        return HttpResponseForbidden("You don't have permission to edit this grade.")

    form = GradeForm(request.POST or None, instance=grade)
    if form.is_valid():
        form.save()
        messages.success(request, 'Grade updated successfully!')
        return redirect('grade_list')
    return render(request, 'students/grade_form.html', {'form': form, 'title': 'Edit Grade', 'grade': grade})


# ==================== FEE MANAGEMENT ====================

@login_required(login_url='login')
def fee_list(request):
    """List fees."""
    if request.user.is_admin():
        fees = Fee.objects.all()
    else:
        # Students can see their own fees
        if hasattr(request.user, 'student_profile'):
            fees = Fee.objects.filter(student=request.user.student_profile)
        else:
            fees = Fee.objects.none()
    
    page = Paginator(fees.order_by('-due_date'), 15).get_page(request.GET.get('page'))
    context = {'fees': page}
    return render(request, 'students/fee_list.html', context)


@login_required(login_url='login')
@admin_only
def fee_create(request):
    """Create a new fee."""
    form = FeeForm(request.POST or None)
    if form.is_valid():
        form.save()
        messages.success(request, 'Fee created successfully!')
        return redirect('fee_list')
    return render(request, 'students/fee_form.html', {'form': form, 'title': 'Create Fee'})


@login_required(login_url='login')
@admin_only
def fee_update(request, fee_id):
    """Update a fee."""
    fee = get_object_or_404(Fee, pk=fee_id)
    form = FeeForm(request.POST or None, instance=fee)
    if form.is_valid():
        form.save()
        messages.success(request, 'Fee updated successfully!')
        return redirect('fee_list')
    return render(request, 'students/fee_form.html', {'form': form, 'title': 'Edit Fee', 'fee': fee})


@login_required(login_url='login')
@admin_only
def fee_delete(request, fee_id):
    """Delete a fee."""
    fee = get_object_or_404(Fee, pk=fee_id)
    if request.method == 'POST':
        fee.delete()
        messages.success(request, 'Fee deleted successfully!')
        return redirect('fee_list')
    return render(request, 'students/fee_confirm_delete.html', {'fee': fee})


# ==================== TRANSCRIPT VIEWS ====================

@login_required(login_url='login')
def transcript_list(request):
    """List academic transcripts."""
    # Get current user's student profile
    try:
        student = request.user.student_profile if hasattr(request.user, 'student_profile') else None
    except Student.DoesNotExist:
        student = None
    
    if request.user.is_student() and student:
        # Students see only their own transcript
        transcript = Transcript.objects.filter(student=student).first()
        context = {
            'transcript': transcript,
            'title': 'My Academic Transcript',
            'is_student': True
        }
        return render(request, 'students/transcript_detail.html', context)
    elif request.user.is_faculty() or request.user.is_admin():
        # Faculty and admin can view all transcripts
        transcripts = Transcript.objects.all().select_related('student')
        
        # Search functionality
        query = request.GET.get('q', '')
        if query:
            transcripts = transcripts.filter(
                Q(student__name__icontains=query) | 
                Q(student__roll_number__icontains=query)
            )
        
        # Pagination
        paginator = Paginator(transcripts, 10)
        page_number = request.GET.get('page')
        transcripts = paginator.get_page(page_number)
        
        context = {
            'transcripts': transcripts,
            'title': 'Academic Transcripts',
            'query': query,
            'is_student': False
        }
        return render(request, 'students/transcript_list.html', context)
    else:
        return HttpResponseForbidden("You don't have permission to view transcripts.")


@login_required(login_url='login')
def transcript_detail(request, student_id):
    """View detailed transcript for a specific student."""
    student = get_object_or_404(Student, pk=student_id)
    transcript = Transcript.objects.filter(student=student).first()
    
    # Check permissions
    student_user = getattr(student, 'user', None)
    if not (request.user.is_admin() or request.user.is_faculty() or request.user == student_user):
        return HttpResponseForbidden("You don't have permission to view this transcript.")
    
    # Get all grades
    grades = Enrollment.objects.filter(student=student, grade__released=True).select_related(
        'course', 'grade'
    ).order_by('course__code')
    
    # Calculate statistics
    context = {
        'student': student,
        'transcript': transcript,
        'grades': grades,
        'title': f'{student.name} - Transcript'
    }
    return render(request, 'students/transcript_detail.html', context)


@login_required(login_url='login')
@admin_only
def transcript_update(request, transcript_id):
    """Update transcript academic standing manually."""
    transcript = get_object_or_404(Transcript, pk=transcript_id)
    form = TranscriptForm(request.POST or None, instance=transcript)
    
    if form.is_valid():
        # Recalculate before saving
        transcript.update_transcript()
        form.save()
        messages.success(request, 'Transcript updated successfully!')
        return redirect('transcript_detail', student_id=transcript.student.id)
    
    context = {
        'form': form,
        'transcript': transcript,
        'title': 'Update Transcript',
        'student': transcript.student
    }
    return render(request, 'students/transcript_form.html', context)


@login_required(login_url='login')
@admin_only
def transcript_regenerate(request, student_id):
    """Regenerate transcript by recalculating GPA and statistics."""
    student = get_object_or_404(Student, pk=student_id)
    transcript, created = Transcript.objects.get_or_create(student=student)
    
    # Recalculate all statistics
    transcript.update_transcript()
    
    messages.success(request, 'Transcript regenerated successfully!')
    return redirect('transcript_detail', student_id=student_id)


# ==================== DEGREE AUDIT VIEWS ====================

@login_required(login_url='login')
def degree_audit_list(request):
    """List degree audits."""
    try:
        student = request.user.student_profile if hasattr(request.user, 'student_profile') else None
    except Student.DoesNotExist:
        student = None
    
    if request.user.is_student() and student:
        # Students see only their own audit
        audit = DegreeAudit.objects.filter(student=student).first()
        context = {
            'audit': audit,
            'title': 'My Degree Audit',
            'is_student': True
        }
        return render(request, 'students/degree_audit_detail.html', context)
    elif request.user.is_faculty() or request.user.is_admin():
        # Faculty and admin can view all audits
        audits = DegreeAudit.objects.all().select_related('student')
        
        # Search functionality
        query = request.GET.get('q', '')
        if query:
            audits = audits.filter(
                Q(student__name__icontains=query) | 
                Q(student__roll_number__icontains=query)
            )
        
        # Pagination
        paginator = Paginator(audits, 10)
        page_number = request.GET.get('page')
        audits = paginator.get_page(page_number)
        
        context = {
            'audits': audits,
            'title': 'Degree Audits',
            'query': query,
            'is_student': False
        }
        return render(request, 'students/degree_audit_list.html', context)
    else:
        return HttpResponseForbidden("You don't have permission to view degree audits.")


@login_required(login_url='login')
def degree_audit_detail(request, student_id):
    """View detailed degree audit for a specific student."""
    student = get_object_or_404(Student, pk=student_id)
    audit = DegreeAudit.objects.filter(student=student).first()
    
    # Check permissions
    student_user = getattr(student, 'user', None)
    if not (request.user.is_admin() or request.user.is_faculty() or request.user == student_user):
        return HttpResponseForbidden("You don't have permission to view this audit.")
    
    # Get completed courses
    completed_courses = Enrollment.objects.filter(
        student=student, 
        grade__released=True,
        grade__grade__in=['A+', 'A', 'B+', 'B', 'C', 'D']
    ).select_related('course', 'grade')
    
    context = {
        'student': student,
        'audit': audit,
        'completed_courses': completed_courses,
        'title': f'{student.name} - Degree Audit'
    }
    return render(request, 'students/degree_audit_detail.html', context)


@login_required(login_url='login')
@admin_only
def degree_audit_update(request, audit_id):
    """Update degree audit requirements."""
    audit = get_object_or_404(DegreeAudit, pk=audit_id)
    form = DegreeAuditForm(request.POST or None, instance=audit)
    
    if form.is_valid():
        # Recalculate progress before saving
        form.save()
        audit.update_progress()
        messages.success(request, 'Degree audit updated successfully!')
        return redirect('degree_audit_detail', student_id=audit.student.id)
    
    context = {
        'form': form,
        'audit': audit,
        'title': 'Update Degree Audit',
        'student': audit.student
    }
    return render(request, 'students/degree_audit_form.html', context)


@login_required(login_url='login')
@admin_only
def degree_audit_update_progress(request, student_id):
    """Recalculate degree audit progress."""
    student = get_object_or_404(Student, pk=student_id)
    audit, created = DegreeAudit.objects.get_or_create(student=student)
    
    # Recalculate progress
    audit.update_progress()
    
    messages.success(request, 'Degree audit progress updated successfully!')
    return redirect('degree_audit_detail', student_id=student_id)


# ==================== FACULTY REPORTS VIEWS ====================

@login_required(login_url='login')
@admin_only
def faculty_reports_dashboard(request):
    """View overall faculty performance reports dashboard."""
    reports = FacultyReport.objects.all().select_related('faculty').order_by('-average_class_gpa')
    
    # Calculate department-wise statistics
    departments = Department.objects.all()
    dept_stats = []
    for dept in departments:
        faculty_in_dept = Faculty.objects.filter(department=dept.code if dept.code != 'CS' else 'cse')
        reports_in_dept = FacultyReport.objects.filter(faculty__in=faculty_in_dept)
        
        if reports_in_dept.exists():
            avg_gpa = sum(r.average_class_gpa for r in reports_in_dept) / reports_in_dept.count()
            dept_stats.append({
                'department': dept.name,
                'faculty_count': faculty_in_dept.count(),
                'avg_gpa': avg_gpa,
                'total_students': sum(r.total_students_taught for r in reports_in_dept),
                'pass_rate': sum(r.pass_rate_percentage for r in reports_in_dept) / reports_in_dept.count()
            })
    
    # Overall statistics
    total_faculty = Faculty.objects.count()
    avg_gpa = sum(r.average_class_gpa for r in reports) / reports.count() if reports.exists() else 0
    total_students_taught = sum(r.total_students_taught for r in reports)
    avg_pass_rate = sum(r.pass_rate_percentage for r in reports) / reports.count() if reports.exists() else 0
    
    context = {
        'reports': reports,
        'dept_stats': dept_stats,
        'total_faculty': total_faculty,
        'avg_gpa': round(avg_gpa, 2),
        'total_students_taught': total_students_taught,
        'avg_pass_rate': round(avg_pass_rate, 1),
        'title': 'Faculty Performance Reports'
    }
    return render(request, 'students/faculty_reports_dashboard.html', context)


@login_required(login_url='login')
def faculty_analytics(request, faculty_id):
    """View detailed analytics for a specific faculty member."""
    faculty = get_object_or_404(Faculty, pk=faculty_id)
    report = FacultyReport.objects.filter(faculty=faculty).first()
    
    # Check permissions - only admin or the faculty member can view
    if not (request.user.is_staff or request.user == faculty.user):
        return HttpResponseForbidden("You don't have permission to view this report.")
    
    # Get courses taught
    courses = faculty.courses_taught.all().prefetch_related('enrollments')
    
    # Calculate per-course analytics
    course_analytics = []
    for course in courses:
        enrollments = course.enrollments.filter(status__in=['enrolled', 'completed'])
        grades = Grade.objects.filter(enrollment__course=course, released=True)
        
        if grades.exists():
            avg_marks = sum(g.total_marks for g in grades) / grades.count()
            pass_count = grades.exclude(grade='F').count()
            fail_count = grades.filter(grade='F').count()
            
            course_analytics.append({
                'course': course,
                'enrollment_count': enrollments.count(),
                'grade_count': grades.count(),
                'avg_marks': round(avg_marks, 1),
                'pass_count': pass_count,
                'fail_count': fail_count,
                'pass_rate': round((pass_count / grades.count() * 100) if grades.count() > 0 else 0, 1)
            })
    
    context = {
        'faculty': faculty,
        'report': report,
        'courses': courses,
        'course_analytics': course_analytics,
        'title': f'{faculty.user.get_full_name()} - Analytics Report'
    }
    return render(request, 'students/faculty_analytics.html', context)


@login_required(login_url='login')
@admin_only
def faculty_performance_compare(request):
    """Compare performance across all faculty members."""
    reports = FacultyReport.objects.all().select_related('faculty').order_by('-average_class_gpa')
    
    # Pagination
    paginator = Paginator(reports, 10)
    page_number = request.GET.get('page')
    reports = paginator.get_page(page_number)
    
    context = {
        'reports': reports,
        'title': 'Faculty Performance Comparison'
    }
    return render(request, 'students/faculty_performance_compare.html', context)


@login_required(login_url='login')
@admin_only
def course_analytics(request, course_id):
    """View detailed analytics for a specific course."""
    course = get_object_or_404(Course, pk=course_id)
    enrollments = Enrollment.objects.filter(course=course).select_related('student', 'grade')
    
    # Grade distribution
    all_grades = Grade.objects.filter(enrollment__course=course, released=True)
    grade_dist = {
        'A': all_grades.filter(grade__in=['A+', 'A']).count(),
        'B': all_grades.filter(grade__in=['B+', 'B']).count(),
        'C': all_grades.filter(grade='C').count(),
        'D': all_grades.filter(grade='D').count(),
        'F': all_grades.filter(grade='F').count(),
    }
    
    # Performance metrics
    if all_grades.exists():
        avg_marks = sum(g.total_marks for g in all_grades) / all_grades.count()
        avg_percentage = sum(g.percentage for g in all_grades) / all_grades.count()
        pass_rate = ((all_grades.count() - grade_dist['F']) / all_grades.count() * 100)
    else:
        avg_marks = 0
        avg_percentage = 0
        pass_rate = 0
    
    # Top and bottom performers
    top_performers = all_grades.order_by('-percentage')[:5]
    bottom_performers = all_grades.order_by('percentage')[:5]
    
    context = {
        'course': course,
        'enrollments': enrollments,
        'all_grades': all_grades,
        'grade_dist': grade_dist,
        'avg_marks': round(avg_marks, 1),
        'avg_percentage': round(avg_percentage, 1),
        'pass_rate': round(pass_rate, 1),
        'top_performers': top_performers,
        'bottom_performers': bottom_performers,
        'title': f'{course.code} - Course Analytics'
    }
    return render(request, 'students/course_analytics.html', context)


@login_required(login_url='login')
@admin_only
def workload_analysis(request):
    """Analyze instructor workload distribution."""
    reports = FacultyReport.objects.all().select_related('faculty').order_by('-total_credits_assigned')
    
    # Calculate workload categories
    high_load = []  # > 12 credits
    medium_load = []  # 6-12 credits
    low_load = []  # < 6 credits
    
    for report in reports:
        if report.total_credits_assigned > 12:
            high_load.append(report)
        elif report.total_credits_assigned >= 6:
            medium_load.append(report)
        else:
            low_load.append(report)
    
    # Calculate statistics
    total_credits_assigned = sum(r.total_credits_assigned for r in reports)
    avg_credits = total_credits_assigned / reports.count() if reports.count() > 0 else 0
    avg_class_size = sum(r.average_class_size for r in reports) / reports.count() if reports.count() > 0 else 0
    
    context = {
        'all_reports': reports,
        'high_load': high_load,
        'medium_load': medium_load,
        'low_load': low_load,
        'total_credits_assigned': total_credits_assigned,
        'avg_credits': round(avg_credits, 1),
        'avg_class_size': round(avg_class_size, 1),
        'title': 'Faculty Workload Analysis'
    }
    return render(request, 'students/workload_analysis.html', context)


# ==================== PDF EXPORT VIEWS ====================

@login_required(login_url='login')
def transcript_pdf(request, transcript_id):
    """
    Generate and download transcript as PDF.
    Allow students to download their own, faculty/admin can download any.
    """
    transcript = get_object_or_404(Transcript, id=transcript_id)
    
    # Check permissions
    if not request.user.is_staff and transcript.student.user != request.user:
        return HttpResponseForbidden("You don't have permission to download this transcript.")
    
    # Generate PDF
    pdf_buffer = generate_transcript_pdf(transcript)
    
    # Create response
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    timestamp = timezone.now().strftime('%Y%m%d%H%M%S')
    filename = f"Transcript_{transcript.student.user.get_full_name().replace(' ', '_')}_{timestamp}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


@login_required(login_url='login')
def faculty_report_pdf(request, report_id):
    """
    Generate and download faculty report as PDF.
    Only admin and faculty can access.
    """
    report = get_object_or_404(FacultyReport, id=report_id)
    
    # Check permissions - only admin and faculty can download
    if not request.user.is_staff and (not hasattr(request.user, 'faculty_profile') or request.user.faculty_profile != report.faculty):
        return HttpResponseForbidden("You don't have permission to download this report.")
    
    # Generate PDF
    pdf_buffer = generate_faculty_report_pdf(report)
    
    # Create response
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    filename = f"Faculty_Report_{report.faculty.user.get_full_name().replace(' ', '_')}.pdf"
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    
    return response


# ==================== NOTIFICATION VIEWS ====================

@login_required(login_url='login')
def notification_list(request):
    """View all notifications for logged-in user."""
    user = request.user
    notifications = Notification.objects.filter(recipient=user).order_by('-created_at')
    
    # Pagination
    paginator = Paginator(notifications, 20)
    page_number = request.GET.get('page')
    notifications = paginator.get_page(page_number)
    
    # Count unread
    unread_count = Notification.objects.filter(recipient=user, is_read=False).count()
    
    context = {
        'title': 'My Notifications',
        'notifications': notifications,
        'unread_count': unread_count,
    }
    return render(request, 'students/notification_list.html', context)


@login_required(login_url='login')
def notification_detail(request, notification_id):
    """View single notification detail."""
    notification = get_object_or_404(Notification, id=notification_id)
    
    # Check permission
    if notification.recipient != request.user and not request.user.is_staff:
        return HttpResponseForbidden("You don't have permission to view this notification.")
    
    # Mark as read
    if not notification.is_read:
        notification.mark_as_read()
    
    context = {
        'title': 'Notification',
        'notification': notification,
    }
    return render(request, 'students/notification_detail.html', context)


@login_required(login_url='login')
@require_http_methods(["POST"])
def notification_mark_read(request, notification_id):
    """Mark notification as read."""
    notification = get_object_or_404(Notification, id=notification_id)
    
    # Check permission
    if notification.recipient != request.user:
        return HttpResponseForbidden("You don't have permission to modify this notification.")
    
    notification.mark_as_read()
    messages.success(request, "Notification marked as read.")
    
    return redirect('notification_list')


@login_required(login_url='login')
@require_http_methods(["POST"])
def notification_mark_unread(request, notification_id):
    """Mark notification as unread."""
    notification = get_object_or_404(Notification, id=notification_id)
    
    # Check permission
    if notification.recipient != request.user:
        return HttpResponseForbidden("You don't have permission to modify this notification.")
    
    notification.is_read = False
    notification.save()
    messages.success(request, "Notification marked as unread.")
    
    return redirect('notification_list')


@login_required(login_url='login')
@require_http_methods(["POST"])
def notification_delete(request, notification_id):
    """Delete a notification."""
    notification = get_object_or_404(Notification, id=notification_id)
    
    # Check permission
    if notification.recipient != request.user:
        return HttpResponseForbidden("You don't have permission to delete this notification.")
    
    notification.delete()
    messages.success(request, "Notification deleted.")
    
    return redirect('notification_list')


@login_required(login_url='login')
@require_http_methods(["POST"])
def notification_mark_all_read(request):
    """Mark all notifications as read."""
    Notification.objects.filter(recipient=request.user, is_read=False).update(
        is_read=True,
        read_at=timezone.now()
    )
    messages.success(request, "All notifications marked as read.")
    
    return redirect('notification_list')


@login_required(login_url='login')
def notification_settings(request):
    """View notification preferences (future feature)."""
    context = {
        'title': 'Notification Settings',
    }
    return render(request, 'students/notification_settings.html', context)

# ==================== LIBRARY MANAGEMENT VIEWS ====================

@login_required(login_url='login')
def library_catalog(request):
    """View catalog of all books."""
    q = request.GET.get('q', '')
    if q:
        books = Book.objects.filter(
            Q(title__icontains=q) | Q(author__icontains=q) | Q(isbn__icontains=q)
        ).order_by('title')
    else:
        books = Book.objects.all().order_by('title')
        
    page = Paginator(books, 12).get_page(request.GET.get('page'))
    
    # Get user's active borrowed books
    active_borrows = BorrowRecord.objects.filter(
        user=request.user, 
        status__in=['active', 'overdue']
    ).select_related('book_instance__book')
    
    # Calculate total fines
    total_fines = sum(b.calculate_fine() for b in active_borrows)
    
    context = {
        'books': page,
        'query': q,
        'active_borrows': active_borrows,
        'total_fines': total_fines,
        'total_books': Book.objects.count()
    }
    return render(request, 'students/library_catalog.html', context)

# ==================== SCHEDULE & EXAMS VIEWS ====================

@login_required(login_url='login')
def schedule_dashboard(request):
    """View timetable and exams for the logged-in user."""
    user = request.user
    
    # Base querysets
    timetable_slots = TimetableSlot.objects.none()
    exams = Exam.objects.none()
    
    if user.role == 'student' and hasattr(user, 'student_profile'):
        # Get courses the student is enrolled in
        enrolled_course_ids = Enrollment.objects.filter(
            student=user.student_profile, status='enrolled'
        ).values_list('course_id', flat=True)
        
        timetable_slots = TimetableSlot.objects.filter(
            course_id__in=enrolled_course_ids
        ).select_related('course', 'classroom')
        
        exams = Exam.objects.filter(
            course_id__in=enrolled_course_ids,
            date__gte=timezone.now().date()
        ).select_related('course', 'classroom').order_by('date', 'start_time')
        
    elif user.role == 'faculty' and hasattr(user, 'faculty_profile'):
        # Get courses taught by the faculty
        taught_course_ids = Course.objects.filter(
            instructor=user.faculty_profile
        ).values_list('id', flat=True)
        
        timetable_slots = TimetableSlot.objects.filter(
            course_id__in=taught_course_ids
        ).select_related('course', 'classroom')
        
        exams = Exam.objects.filter(
            course_id__in=taught_course_ids,
            date__gte=timezone.now().date()
        ).select_related('course', 'classroom').order_by('date', 'start_time')
        
    # Group timetable by day for the template grid
    days = ['MON', 'TUE', 'WED', 'THU', 'FRI', 'SAT']
    grouped_timetable = {day: [] for day in days}
    for slot in timetable_slots:
        grouped_timetable[slot.day_of_week].append(slot)
        
    context = {
        'grouped_timetable': grouped_timetable,
        'exams': exams,
    }
    return render(request, 'students/schedule_dashboard.html', context)

# ==================== LEAVE MANAGEMENT VIEWS ====================

@login_required(login_url='login')
def leave_dashboard(request):
    """View leave history and submit new requests."""
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        reason = request.POST.get('reason')
        
        if start_date and end_date and reason:
            LeaveRequest.objects.create(
                user=request.user,
                start_date=start_date,
                end_date=end_date,
                reason=reason
            )
            messages.success(request, 'Leave request submitted successfully.')
            return redirect('leave_dashboard')
        else:
            messages.error(request, 'Please fill in all required fields.')
            
    # Existing requests
    leaves = LeaveRequest.objects.filter(user=request.user).order_by('-applied_on')
    
    context = {
        'leaves': leaves,
    }
    return render(request, 'students/leave_dashboard.html', context)
