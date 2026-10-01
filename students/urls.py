from django.urls import path

from . import views

urlpatterns = [
    # ==================== AUTHENTICATION ====================
    path('login/', views.user_login, name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('register/', views.user_signup, name='register'),
    path('faculty-profile-setup/', views.faculty_profile_setup, name='faculty_profile_setup'),
    
    # ==================== DASHBOARDS ====================
    path('dashboard/', views.dashboard, name='dashboard'),
    path('admin/dashboard/', views.admin_dashboard, name='admin_dashboard'),
    path('faculty/dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('portal/', views.student_portal, name='student_portal'),  # Alias for student dashboard
    
    # ==================== STUDENT MANAGEMENT ====================
    path('', views.student_list, name='student_list'),
    path('create/', views.student_create, name='student_create'),
    path('update/<int:student_id>/', views.student_update, name='student_update'),
    path('delete/<int:student_id>/', views.student_delete, name='student_delete'),
    
    # ==================== DEPARTMENT MANAGEMENT ====================
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/update/<int:dept_id>/', views.department_update, name='department_update'),
    path('departments/delete/<int:dept_id>/', views.department_delete, name='department_delete'),
    
    # ==================== COURSE MANAGEMENT ====================
    path('courses/', views.course_list, name='course_list'),
    path('courses/create/', views.course_create, name='course_create'),
    path('courses/update/<int:course_id>/', views.course_update, name='course_update'),
    path('courses/delete/<int:course_id>/', views.course_delete, name='course_delete'),
    
    # ==================== ENROLLMENT MANAGEMENT ====================
    path('enrollments/', views.enrollment_list, name='enrollment_list'),
    path('enrollments/create/', views.enrollment_create, name='enrollment_create'),
    path('enrollments/update/<int:enroll_id>/', views.enrollment_update, name='enrollment_update'),
    path('enrollments/delete/<int:enroll_id>/', views.enrollment_delete, name='enrollment_delete'),
    
    # ==================== ATTENDANCE MANAGEMENT ====================
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/record/', views.attendance_record, name='attendance_record'),
    path('attendance/update/<int:record_id>/', views.attendance_update, name='attendance_update'),
    
    # ==================== GRADE MANAGEMENT ====================
    path('grades/', views.grade_list, name='grade_list'),
    path('grades/create/<int:enroll_id>/', views.grade_create, name='grade_create'),
    path('grades/update/<int:grade_id>/', views.grade_update, name='grade_update'),
    
    # ==================== FEE MANAGEMENT ====================
    path('fees/', views.fee_list, name='fee_list'),
    path('fees/create/', views.fee_create, name='fee_create'),
    path('fees/update/<int:fee_id>/', views.fee_update, name='fee_update'),
    path('fees/delete/<int:fee_id>/', views.fee_delete, name='fee_delete'),
    
    # ==================== TRANSCRIPT MANAGEMENT ====================
    path('transcripts/', views.transcript_list, name='transcript_list'),
    path('transcripts/<int:student_id>/', views.transcript_detail, name='transcript_detail'),
    path('transcripts/update/<int:transcript_id>/', views.transcript_update, name='transcript_update'),
    path('transcripts/regenerate/<int:student_id>/', views.transcript_regenerate, name='transcript_regenerate'),
    
    # ==================== DEGREE AUDIT MANAGEMENT ====================
    path('degree-audits/', views.degree_audit_list, name='degree_audit_list'),
    path('degree-audits/<int:student_id>/', views.degree_audit_detail, name='degree_audit_detail'),
    path('degree-audits/update/<int:audit_id>/', views.degree_audit_update, name='degree_audit_update'),
    path('degree-audits/update-progress/<int:student_id>/', views.degree_audit_update_progress, name='degree_audit_update_progress'),
    
    # ==================== FACULTY REPORTS ====================
    path('reports/faculty/', views.faculty_reports_dashboard, name='faculty_reports_dashboard'),
    path('reports/faculty/<int:faculty_id>/', views.faculty_analytics, name='faculty_analytics'),
    path('reports/faculty-comparison/', views.faculty_performance_compare, name='faculty_performance_compare'),
    path('reports/course/<int:course_id>/', views.course_analytics, name='course_analytics'),
    path('reports/workload/', views.workload_analysis, name='workload_analysis'),
    
    # ==================== PDF EXPORTS ====================
    path('transcripts/<int:transcript_id>/pdf/', views.transcript_pdf, name='transcript_pdf'),
    path('reports/faculty/<int:report_id>/pdf/', views.faculty_report_pdf, name='faculty_report_pdf'),
    
    # ==================== NOTIFICATIONS ====================
    path('notifications/', views.notification_list, name='notification_list'),
    path('notifications/<int:notification_id>/', views.notification_detail, name='notification_detail'),
    path('notifications/<int:notification_id>/mark-read/', views.notification_mark_read, name='notification_mark_read'),
    path('notifications/<int:notification_id>/mark-unread/', views.notification_mark_unread, name='notification_mark_unread'),
    path('notifications/<int:notification_id>/delete/', views.notification_delete, name='notification_delete'),
    path('notifications/mark-all-read/', views.notification_mark_all_read, name='notification_mark_all_read'),
    path('notifications/settings/', views.notification_settings, name='notification_settings'),
    
    # ==================== LIBRARY MANAGEMENT ====================
    path('library/', views.library_catalog, name='library_catalog'),
    
    # ==================== SCHEDULE & EXAMS ====================
    path('schedule/', views.schedule_dashboard, name='schedule_dashboard'),
    
    # ==================== LEAVE MANAGEMENT ====================
    path('leave/', views.leave_dashboard, name='leave_dashboard'),
]