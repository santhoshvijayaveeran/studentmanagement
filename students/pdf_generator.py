"""
PDF Generation utilities for transcripts and faculty reports
"""
from io import BytesIO
from datetime import datetime
from reportlab.lib.pagesizes import letter, A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT


def generate_transcript_pdf(transcript):
    """
    Generate a professional PDF transcript for a student
    
    Args:
        transcript: Transcript model instance
        
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=0.5*inch, leftMargin=0.5*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=24,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#374151'),
        spaceAfter=8,
        fontName='Helvetica-Bold',
        borderColor=colors.HexColor('#e5e7eb'),
        borderWidth=1,
        borderPadding=6,
        borderRadius=3
    )
    
    # Document elements
    elements = []
    
    # Title
    elements.append(Paragraph("OFFICIAL ACADEMIC TRANSCRIPT", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Student Information
    student = transcript.student
    student_name = student.user.get_full_name() if student.user else student.name
    student_email = student.user.email if student.user else student.email
    student_id = student.user.username if student.user else student.roll_number
    
    info_data = [
        ['Student Name:', student_name, 'Student ID:', student_id],
        ['Email:', student_email, 'Department:', student.get_department_display()],
        ['Date of Issue:', datetime.now().strftime('%B %d, %Y'), 
         'Cumulative GPA:', f"{transcript.cumulative_gpa}"],
    ]
    
    info_table = Table(info_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#111827')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Academic Summary
    elements.append(Paragraph("ACADEMIC SUMMARY", heading_style))
    
    summary_data = [
        ['Metric', 'Value'],
        ['Cumulative GPA', f"{transcript.cumulative_gpa}/4.0"],
        ['Total Credits Completed', str(transcript.total_credits_completed)],
        ['Total Credits Attempted', str(transcript.total_credits_attempted)],
        ['Courses Passed', str(transcript.total_courses_passed)],
        ['Courses Failed', str(transcript.total_courses_failed)],
        ['Cumulative Percentage', f"{transcript.cumulative_percentage}%"],
        ['Academic Standing', transcript.get_academic_standing_display()],
    ]
    
    summary_table = Table(summary_data, colWidths=[3.5*inch, 2.5*inch])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Course Grades
    elements.append(Paragraph("COURSE GRADES", heading_style))
    
    course_grades = transcript.student.enrollments.filter(
        grade__isnull=False
    ).select_related('course', 'grade')
    
    if course_grades:
        grade_data = [
            ['Course Code', 'Course Name', 'Credits', 'Grade', 'Percentage', 'Status']
        ]
        
        for enrollment in course_grades:
            grade = enrollment.grade
            status = 'PASSED' if float(grade.percentage) >= 40 else 'FAILED'
            status_color = colors.HexColor('#10b981') if status == 'PASSED' else colors.HexColor('#ef4444')
            
            grade_data.append([
                enrollment.course.code,
                enrollment.course.name[:30],
                str(enrollment.course.credits),
                grade.grade,
                f"{grade.percentage}%",
                status
            ])
        
        grade_table = Table(grade_data, colWidths=[0.8*inch, 2.2*inch, 0.7*inch, 0.6*inch, 0.8*inch, 0.9*inch])
        grade_table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('ALIGN', (1, 0), (1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
            ('TOPPADDING', (0, 0), (-1, -1), 5),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
        ]))
        elements.append(grade_table)
    else:
        elements.append(Paragraph("No grades have been entered yet.", styles['Normal']))
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_text = "This is an official academic transcript issued by the University."
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_faculty_report_pdf(faculty_report):
    """
    Generate a professional PDF faculty performance report
    
    Args:
        faculty_report: FacultyReport model instance
        
    Returns:
        BytesIO object containing the PDF
    """
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter,
                           rightMargin=0.5*inch, leftMargin=0.5*inch,
                           topMargin=0.75*inch, bottomMargin=0.75*inch)
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=22,
        textColor=colors.HexColor('#1f2937'),
        spaceAfter=12,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )
    
    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=colors.HexColor('#374151'),
        spaceAfter=8,
        fontName='Helvetica-Bold'
    )
    
    elements = []
    
    # Title
    elements.append(Paragraph("FACULTY PERFORMANCE REPORT", title_style))
    elements.append(Spacer(1, 0.2*inch))
    
    # Faculty Information
    faculty = faculty_report.faculty
    info_data = [
        ['Faculty Name:', str(faculty.user.get_full_name()), 'Employee ID:', faculty.employee_id],
        ['Department:', faculty.get_department_display(), 'Report Date:', faculty_report.last_updated.strftime('%B %d, %Y')],
        ['Specialization:', faculty.specialization, 'Avg Class GPA:', f"{faculty_report.average_class_gpa}"],
    ]
    
    info_table = Table(info_data, colWidths=[1.2*inch, 2.3*inch, 1.2*inch, 2.3*inch])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), colors.HexColor('#f3f4f6')),
        ('TEXTCOLOR', (0, 0), (-1, -1), colors.HexColor('#111827')),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Teaching Statistics
    elements.append(Paragraph("TEACHING STATISTICS", heading_style))
    
    stats_data = [
        ['Metric', 'Value'],
        ['Total Courses Taught', str(faculty_report.total_courses_taught)],
        ['Current Semester Courses', str(faculty_report.current_semester_courses)],
        ['Total Students Taught', str(faculty_report.total_students_taught)],
        ['Current Semester Students', str(faculty_report.current_semester_students)],
        ['Average Class Size', f"{faculty_report.average_class_size} students"],
    ]
    
    stats_table = Table(stats_data, colWidths=[3.5*inch, 2.5*inch])
    stats_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    elements.append(stats_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Grade Statistics
    elements.append(Paragraph("GRADE STATISTICS", heading_style))
    
    grade_stats_data = [
        ['Metric', 'Value'],
        ['Average Class GPA', f"{faculty_report.average_class_gpa}/4.0"],
        ['Most Common Grade', faculty_report.average_grades_given],
        ['Pass Rate', f"{faculty_report.pass_rate_percentage}%"],
        ['Fail Rate', f"{faculty_report.fail_rate_percentage}%"],
        ['Student Satisfaction Score', f"{faculty_report.student_satisfaction_score}/5.0" if faculty_report.student_satisfaction_score else 'N/A'],
    ]
    
    grade_table = Table(grade_stats_data, colWidths=[3.5*inch, 2.5*inch])
    grade_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    elements.append(grade_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Grade Distribution
    elements.append(Paragraph("GRADE DISTRIBUTION", heading_style))
    
    grade_dist_data = [
        ['Grade', 'Count'],
        ['A+/A', str(faculty_report.grade_a_count)],
        ['B+/B', str(faculty_report.grade_b_count)],
        ['C', str(faculty_report.grade_c_count)],
        ['D', str(faculty_report.grade_d_count)],
        ['F', str(faculty_report.grade_f_count)],
    ]
    
    dist_table = Table(grade_dist_data, colWidths=[3.5*inch, 2.5*inch])
    dist_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    elements.append(dist_table)
    elements.append(Spacer(1, 0.25*inch))
    
    # Workload Information
    elements.append(Paragraph("WORKLOAD ANALYSIS", heading_style))
    
    workload_data = [
        ['Metric', 'Value'],
        ['Total Credits Assigned', f"{faculty_report.total_credits_assigned} credits"],
        ['Peak Semester Load', f"{faculty_report.peak_semester_load} credits"],
        ['Workload Level', 'High' if faculty_report.total_credits_assigned > 12 else ('Medium' if faculty_report.total_credits_assigned >= 6 else 'Low')],
    ]
    
    workload_table = Table(workload_data, colWidths=[3.5*inch, 2.5*inch])
    workload_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f2937')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#d1d5db')),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f9fafb')]),
    ]))
    elements.append(workload_table)
    
    elements.append(Spacer(1, 0.3*inch))
    
    # Footer
    footer_text = "This report is automatically generated by the Academic Management System."
    footer_style = ParagraphStyle(
        'Footer',
        parent=styles['Normal'],
        fontSize=8,
        textColor=colors.HexColor('#6b7280'),
        alignment=TA_CENTER
    )
    elements.append(Paragraph(footer_text, footer_style))
    
    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
