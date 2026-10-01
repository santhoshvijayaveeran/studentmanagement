from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth import authenticate

from .models import User, Student, Faculty, Department, Course, Enrollment, Attendance, Grade, Fee, Transcript, DegreeAudit


class UserLoginForm(forms.Form):
    """Form for user login."""
    
    username = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={
            'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all',
            'placeholder': 'Username',
            'autofocus': True
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all',
            'placeholder': 'Password'
        })
    )
    
    def clean(self):
        username = self.cleaned_data.get('username')
        password = self.cleaned_data.get('password')
        
        if username and password:
            self.user_cache = authenticate(username=username, password=password)
            if self.user_cache is None:
                raise forms.ValidationError("Invalid username or password.")
        return self.cleaned_data
    
    def get_user(self):
        return self.user_cache


class UserSignupForm(UserCreationForm):
    """Form for user registration."""
    
    ROLE_CHOICES = [
        ('student', 'Register as Student'),
        ('faculty', 'Register as Faculty'),
    ]
    
    role = forms.ChoiceField(
        choices=ROLE_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'w-4 h-4 rounded border-outline-variant text-primary focus:ring-primary/30 focus:ring-2'}),
        initial='student'
    )
    
    first_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'First Name'})
    )
    
    last_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Last Name'})
    )
    
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Email Address'})
    )
    
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Phone Number'})
    )
    
    department = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Department'})
    )
    
    class Meta:
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'phone', 'department', 'role', 'password1', 'password2')
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Username'})
        self.fields['password1'].widget.attrs.update({'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Password'})
        self.fields['password2'].widget.attrs.update({'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Confirm Password'})
        
        # Remove help texts
        self.fields['username'].help_text = ''
        self.fields['password1'].help_text = ''
        self.fields['password2'].help_text = ''
    
    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if phone:
            normalized = ''.join(ch for ch in phone if ch.isdigit() or ch in '+- ()')
            if len([ch for ch in normalized if ch.isdigit()]) < 7:
                raise forms.ValidationError('Please enter a valid phone number.')
        return phone
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = self.cleaned_data.get('role', 'student')
        user.phone = self.cleaned_data.get('phone', '')
        user.department = self.cleaned_data.get('department', '')
        if commit:
            user.save()
        return user


class FacultyForm(forms.ModelForm):
    """Form for faculty profile creation."""
    
    class Meta:
        model = Faculty
        fields = ['employee_id', 'department', 'specialization', 'experience_years', 'office_location', 'phone']
        widgets = {
            'employee_id': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Employee ID'}),
            'department': forms.Select(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all'}),
            'specialization': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Specialization'}),
            'experience_years': forms.NumberInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'min': 0}),
            'office_location': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Office Location'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Phone Number'}),
        }


class DepartmentForm(forms.ModelForm):
    """Form for department management."""
    
    class Meta:
        model = Department
        fields = ['code', 'name', 'description', 'hod', 'total_seats']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'e.g., CSE'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Department Name'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'rows': 3}),
            'hod': forms.Select(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all'}),
            'total_seats': forms.NumberInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'min': 1}),
        }


class CourseForm(forms.ModelForm):
    """Form for course management."""
    
    class Meta:
        model = Course
        fields = ['code', 'name', 'description', 'department', 'instructor', 'semester', 'credits', 'capacity', 'room', 'schedule']
        widgets = {
            'code': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'e.g., CS101'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Course Name'}),
            'description': forms.Textarea(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'rows': 3}),
            'department': forms.Select(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all'}),
            'instructor': forms.Select(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all'}),
            'semester': forms.Select(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all'}),
            'credits': forms.NumberInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'min': 1, 'max': 6}),
            'capacity': forms.NumberInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'min': 1}),
            'room': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'e.g., A101'}),
            'schedule': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'e.g., MWF 10:00-11:00'}),
        }


class EnrollmentForm(forms.ModelForm):
    """Form for course enrollment."""
    
    class Meta:
        model = Enrollment
        fields = ['student', 'course', 'semester_year']
        widgets = {
            'student': forms.Select(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all'}),
            'course': forms.Select(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all'}),
            'semester_year': forms.NumberInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'min': 2000, 'max': 2100}),
        }


class AttendanceForm(forms.ModelForm):
    """Form for attendance recording."""
    
    class Meta:
        model = Attendance
        fields = ['enrollment', 'date', 'status', 'remarks']
        widgets = {
            'enrollment': forms.Select(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all'}),
            'date': forms.DateInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'type': 'date'}),
            'status': forms.Select(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all'}),
            'remarks': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Optional remarks'}),
        }


class GradeForm(forms.ModelForm):
    """Form for grade management."""
    
    class Meta:
        model = Grade
        fields = ['internal_marks', 'external_marks', 'remarks', 'released']
        widgets = {
            'internal_marks': forms.NumberInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'min': 0, 'max': 40, 'placeholder': 'Out of 40'}),
            'external_marks': forms.NumberInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'min': 0, 'max': 60, 'placeholder': 'Out of 60'}),
            'remarks': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Optional remarks'}),
            'released': forms.CheckboxInput(attrs={'class': 'w-4 h-4 rounded border-outline-variant text-primary focus:ring-primary/30 focus:ring-2'}),
        }


class FeeForm(forms.ModelForm):
    """Form for fee management."""
    
    class Meta:
        model = Fee
        fields = ['student', 'fee_type', 'amount', 'due_date', 'paid_amount', 'payment_status', 'semester', 'year', 'remarks']
        widgets = {
            'student': forms.Select(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all'}),
            'fee_type': forms.Select(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all'}),
            'amount': forms.NumberInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'min': 0, 'step': '0.01'}),
            'due_date': forms.DateInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'type': 'date'}),
            'paid_amount': forms.NumberInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'min': 0, 'step': '0.01'}),
            'payment_status': forms.Select(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all'}),
            'semester': forms.NumberInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'min': 1, 'max': 8}),
            'year': forms.NumberInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'min': 2000, 'max': 2100}),
            'remarks': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Optional remarks'}),
        }


class StudentForm(forms.ModelForm):
    """Form for student profile creation/update."""
    
    enrollment_year = forms.IntegerField(
        widget=forms.NumberInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'min': 2000, 'max': 2100})
    )
    
    class Meta:
        model = Student
        fields = [
            'name',
            'roll_number',
            'email',
            'phone',
            'department',
            'date_of_birth',
            'enrollment_year',
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all'}),
            'name': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Full Name'}),
            'roll_number': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Roll Number'}),
            'email': forms.EmailInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Phone'}),
            'department': forms.Select(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all'}),
        }


class TranscriptForm(forms.ModelForm):
    """Form for transcript management."""
    
    class Meta:
        model = Transcript
        fields = ['academic_standing']
        widgets = {
            'academic_standing': forms.Select(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all'}),
        }


class DegreeAuditForm(forms.ModelForm):
    """Form for degree audit management."""
    
    class Meta:
        model = DegreeAudit
        fields = [
            'degree_name',
            'total_credits_required',
            'core_courses_required',
            'elective_courses_required',
            'expected_graduation',
        ]
        widgets = {
            'degree_name': forms.TextInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'placeholder': 'Degree Name'}),
            'total_credits_required': forms.NumberInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'min': 0}),
            'core_courses_required': forms.NumberInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'min': 0}),
            'elective_courses_required': forms.NumberInput(attrs={'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all', 'min': 0}),
            'expected_graduation': forms.DateInput(attrs={'type': 'date', 'class': 'w-full px-3 py-2.5 rounded-lg border border-outline-variant/60 bg-surface-container-lowest text-on-surface font-body-sm text-body-sm placeholder:text-outline focus:outline-none focus:border-primary focus:ring-4 focus:ring-primary/15 transition-all'}),
        }

    def clean_phone(self):
        phone = self.cleaned_data.get('phone', '').strip()
        if not phone:
            raise forms.ValidationError('Please enter a phone number.')
        normalized = ''.join(ch for ch in phone if ch.isdigit() or ch in '+- ()')
        if len([ch for ch in normalized if ch.isdigit()]) < 7:
            raise forms.ValidationError('Please enter a valid phone number.')
        return phone
