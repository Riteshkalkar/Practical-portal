import os
from django.http import JsonResponse
import zipfile
from datetime import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponse, Http404, JsonResponse
from django.core.files.base import ContentFile
from django.utils import timezone
from docx import Document
from docx.shared import Inches
from PIL import Image as PILImage
from io import BytesIO
from .models import CustomUser, Subject, Practical, PracticalSubmission, Certificate, ExamMode, CertificateSubmission
from .forms import (StudentRegistrationForm, TeacherRegistrationForm, HODRegistrationForm, 
                   ExaminerCreationForm, CustomLoginForm, SubjectForm, PracticalForm, 
                   PracticalSubmissionForm, FeedbackForm, ExamModeForm, ExaminerSearchForm,CertificateSubmissionForm)
from .forms import CustomLoginForm 
from .utils import get_google_docs_viewer_url, get_file_extension, is_viewable_file, get_file_icon 
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.shortcuts import render, redirect




def home(request):
    """Home page showing public best practicals"""
    
    exam_modes = ExamMode.objects.filter(is_enabled=True)

    if exam_modes.exists():
        public_practicals = []
    else:
       
        public_practicals = PracticalSubmission.objects.filter(
            status='approved',
            practical__is_public=True
        ).select_related(
            'student',
            'practical',
            'practical__subject',
            'practical__teacher'
        )

    return render(request, 'portal/home.html', {
        'public_practicals': public_practicals,
        'exam_mode_enabled': exam_modes.exists()
    })


def student_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST, request=request, role='student')
        if form.is_valid():
            login(request, form.user)
            return redirect('student_dashboard')
    else:
        form = CustomLoginForm(role='student')
    return render(request, 'portal/auth/student_login.html', {'form': form})

def teacher_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST, request=request, role='teacher')
        if form.is_valid():
            login(request, form.user)
            return redirect('teacher_dashboard')
    else:
        form = CustomLoginForm(role='teacher')
    return render(request, 'portal/auth/teacher_login.html', {'form': form})

def hod_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST, request=request, role='hod')
        if form.is_valid():
            login(request, form.user)
            return redirect('hod_dashboard')
    else:
        form = CustomLoginForm(role='hod')
    return render(request, 'portal/auth/hod_login.html', {'form': form})

def admin_login(request):
    if request.method == 'POST':
        form = CustomLoginForm(request.POST, request=request, role='admin')
        if form.is_valid():
            login(request, form.user)
            return redirect('admin_dashboard')
    else:
        form = CustomLoginForm(role='admin')
    return render(request, 'portal/auth/admin_login.html', {'form': form})

def examiner_login(request):
    """
    Examiner login view with role-based authentication.
    """
    if request.method == 'POST':
        form = CustomLoginForm(request.POST, request=request, role='examiner')
        if form.is_valid():
            login(request, form.user)
            messages.success(request, f"Welcome, {form.user.full_name}!")
            return redirect('examiner_dashboard')
        else:
            
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, error)
    else:
        form = CustomLoginForm(role='examiner')

    context = {
        'form': form,
        'page_title': 'Examiner Login',
        'description': 'Please enter your credentials to access the Examiner Dashboard.'
    }
    return render(request, 'portal/auth/examiner_login.html', context)

def student_register(request):
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('student_login')
    else:
        form = StudentRegistrationForm()
    return render(request, 'portal/auth/student_register.html', {'form': form})

def teacher_register(request):
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Please login.')
            return redirect('hod_dashboard')
    else:
        form = TeacherRegistrationForm()
    return render(request, 'portal/auth/teacher_register.html', {'form': form})

def hod_register(request):
    if request.method == 'POST':
        form = HODRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Registration successful! Admin will assign your department.')
            return redirect('hod_dashboard')
    else:
        form = HODRegistrationForm()
    return render(request, 'portal/auth/hod_register.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('home')


@login_required
def student_dashboard(request):
    if request.user.role != 'student':
        messages.error(request, 'Access denied')
        return redirect('home')

    exam_mode_enabled = ExamMode.objects.filter(
        department=request.user.department, is_enabled=True
    ).exists()

    subjects = Subject.objects.filter(
        department=request.user.department,
        student_class=request.user.student_class
    ).select_related('teacher')

    practicals = Practical.objects.filter(
        subject__in=subjects
    ).select_related('subject').order_by('subject', 'number')
    
    print(f"Student: {request.user.full_name}")
    print(f"Department: {request.user.department}")
    print(f"Class: {request.user.student_class}")
    print(f"Subjects found: {subjects.count()}")
    print(f"Practicals found: {practicals.count()}")
    
    
    submissions = PracticalSubmission.objects.filter(student=request.user).select_related('practical')

  
    practical_status = {practical.id: submissions.filter(practical=practical).first() for practical in practicals}

    
    certificates = Certificate.objects.filter(
        student=request.user
    ).select_related('subject', 'teacher', 'hod')
    
    
    available_certificates = Certificate.objects.filter(
        subject__in=subjects,
        student__isnull=True,
        status__in=['template_added', 'generated']
    ).select_related('subject', 'teacher', 'hod')
    
   
    all_certificates = certificates.union(available_certificates)

    context = {
        'subjects': subjects,
        'practicals': practicals,
        'practical_status': practical_status, 
        'submissions': submissions,
        'certificates': all_certificates,
        'exam_mode_enabled': exam_mode_enabled,
    }

    return render(request, 'portal/dashboards/student_dashboard.html', context)



@login_required
def teacher_dashboard(request):
    
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('home')
    
    subjects = Subject.objects.filter(teacher=request.user)
    practicals = Practical.objects.filter(teacher=request.user)
    submissions = (
        PracticalSubmission.objects.filter(
            practical__teacher=request.user,
            is_draft=False
        )
        .select_related('student', 'practical')
    )

   
    certificates = (
        Certificate.objects.filter(teacher=request.user)
        .select_related('subject')
    )

    
    certificate_submissions = (
        CertificateSubmission.objects.filter(certificate__teacher=request.user)
        .select_related('student', 'certificate')
    )

    
    context = {
        'subjects': subjects,
        'practicals': practicals,
        'submissions': submissions,
        'certificates': certificates,
        'certificate_submissions': certificate_submissions,
    }

    return render(request, 'portal/dashboards/teacher_dashboard.html', context)

@login_required
def hod_dashboard(request):
    if request.user.role != 'hod':
        messages.error(request, 'Access denied')
        return redirect('home')
    
    if not request.user.department:
        messages.warning(request, 'Your department has not been assigned yet. Please contact admin.')
        return render(request, 'portal/dashboards/hod_dashboard.html', {'no_department': True})
    
    students = CustomUser.objects.filter(role='student', department=request.user.department)
    teachers = CustomUser.objects.filter(role='teacher', department=request.user.department)
    subjects = Subject.objects.filter(department=request.user.department)
    certificates = Certificate.objects.filter(
        subject__department=request.user.department,
        status='sent_to_hod'
    ).select_related('student', 'subject', 'teacher')
    
    exam_mode, created = ExamMode.objects.get_or_create(
        department=request.user.department,
        defaults={'is_enabled': False}
    )
    
    return render(request, 'portal/dashboards/hod_dashboard.html', {
        'students': students,
        'teachers': teachers,
        'subjects': subjects,
        'certificates': certificates,
        'exam_mode': exam_mode
    })

@login_required
def admin_dashboard(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('home')
    
    students = CustomUser.objects.filter(role='student')
    teachers = CustomUser.objects.filter(role='teacher')
    hods = CustomUser.objects.filter(role='hod')
    examiners = CustomUser.objects.filter(role='examiner')
    subjects = Subject.objects.all()
    submissions = PracticalSubmission.objects.filter(is_draft=False)
    
    return render(request, 'portal/dashboards/admin_dashboard.html', {
        'students': students,
        'teachers': teachers,
        'hods': hods,
        'examiners': examiners,
        'subjects': subjects,
        'submissions': submissions
    })


@login_required
def examiner_dashboard(request):
    if request.user.role != 'examiner':
        messages.error(request, 'Access denied')
        return redirect('home')
    
    form = ExaminerSearchForm(request.POST or None)
    student_data = None
    
    if request.method == 'POST' and form.is_valid():
        department = form.cleaned_data.get('department')
        student_class = form.cleaned_data.get('student_class')
        roll_number = form.cleaned_data.get('roll_number').strip() if form.cleaned_data.get('roll_number') else None
        subject = form.cleaned_data.get('subject')

      
        if not department or not student_class or not roll_number:
            messages.error(request, 'Please provide Department, Class, and Roll Number')
        else:
           
            student = CustomUser.objects.filter(
                role='student',
                department=department,
                student_class=student_class,
                roll_number=roll_number
            ).first()

            if not student:
                messages.error(request, 'No student found with the given details')
            else:
               
                submissions = PracticalSubmission.objects.filter(student=student)
                if subject:
                    submissions = submissions.filter(practical__subject=subject)
                submissions = submissions.select_related('practical', 'practical__subject')

                
                certificate = None
                if subject:
                    certificate = Certificate.objects.filter(student=student, subject=subject).first()
                else:
                    certificate = Certificate.objects.filter(student=student).first()

                
                student_data = {
                    'student': student,
                    'submissions': submissions,
                    'certificate': certificate
                }

    context = {
        'form': form,
        'student_data': student_data
    }

    return render(request, 'portal/dashboards/examiner_dashboard.html', context)


@login_required
def add_subject(request):
    if request.user.role not in ['admin', 'hod']:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    if request.method == 'POST':
        form = SubjectForm(request.POST)
        if form.is_valid():
            subject = form.save(commit=False)
            if request.user.role == 'hod':
                subject.department = request.user.department
                if subject.teacher.department != request.user.department:
                    messages.error(request, 'You can only assign teachers from your department')
                    return render(request, 'portal/subjects/add_subject.html', {'form': form})
            subject.save()
            messages.success(request, 'Subject added successfully')
            return redirect(f'{request.user.role}_dashboard')
    else:
        form = SubjectForm()
        if request.user.role == 'hod':
            form.fields['teacher'].queryset = CustomUser.objects.filter(
                role='teacher',
                department=request.user.department
            )
    
    return render(request, 'portal/subjects/add_subject.html', {'form': form})


@login_required
def add_practical(request, subject_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('home')
    
    subject = get_object_or_404(Subject, id=subject_id, teacher=request.user)
    
    if request.method == 'POST':
        form = PracticalForm(request.POST)
        if form.is_valid():
            practical = form.save(commit=False)
            practical.subject = subject
            practical.teacher = request.user
            practical.save()
            messages.success(request, 'Practical added successfully')
            return redirect('teacher_dashboard')
    else:
        form = PracticalForm()
    
    return render(request, 'portal/practicals/add_practical.html', {
        'form': form, 
        'subject': subject
    })

@login_required
def practical_detail(request, practical_id):
    practical = get_object_or_404(Practical, id=practical_id)
    
 
    if request.user.role == 'student':
        if (practical.subject.department != request.user.department or 
            practical.subject.student_class != request.user.student_class):
            messages.error(request, 'Access denied')
            return redirect('student_dashboard')
    elif request.user.role == 'teacher':
        if practical.teacher != request.user:
            messages.error(request, 'Access denied')
            return redirect('teacher_dashboard')
    
    submission = None
    if request.user.role == 'student':
        submission = PracticalSubmission.objects.filter(
            student=request.user, 
            practical=practical
        ).first()
    
    return render(request, 'portal/practicals/practical_detail.html', {
        'practical': practical,
        'submission': submission
    })

@login_required
def submit_practical(request, practical_id):
    student = request.user
    practical = get_object_or_404(Practical, id=practical_id)

    
    submission, created = PracticalSubmission.objects.get_or_create(
        student=student,
        practical=practical
    )

    if request.method == 'POST':
        form = PracticalSubmissionForm(request.POST, request.FILES, instance=submission)
        action = request.POST.get('action')

        if form.is_valid():
            practical_submission = form.save(commit=False)
            practical_submission.student = student
            practical_submission.practical = practical

            
            if action == 'final_submit':
                practical_submission.is_draft = False
                practical_submission.status = 'submitted'   
            else:
                practical_submission.is_draft = True
                practical_submission.status = 'draft'

            practical_submission.save()
            return redirect('student_dashboard')
    else:
        form = PracticalSubmissionForm(instance=submission)

    context = {
        'practical': practical,
        'submission': submission,
        'form': form
    }
    return render(request, 'portal/practicals/submit_practical.html', context)
@login_required
def review_submission(request, submission_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('home')
    
    submission = get_object_or_404(
        PracticalSubmission,
        id=submission_id,
        practical__teacher=request.user
    )
    
    if request.method == 'POST':
        action = request.POST.get('action')
        feedback_form = FeedbackForm(request.POST)
        
        if feedback_form.is_valid():
            feedback = feedback_form.cleaned_data['feedback']
            
            if action == 'approve':
                submission.status = 'approved'
                submission.approved_at = timezone.now()
                submission.feedback = feedback
                messages.success(request, 'Submission approved successfully ✅')
            
            elif action == 'reject':
                submission.status = 'rejected'
                submission.feedback = feedback
                messages.success(request, 'Submission rejected ❌')
            
            submission.save()
            return redirect('teacher_dashboard')
    else:
        feedback_form = FeedbackForm()

    # ✅ Build absolute file URL for smart viewer (PDF.js / DOCX.js / fallback)
    file_url = None
    if submission.file_path:
        try:
            file_url = request.build_absolute_uri(submission.file_path.url)
        except Exception:
            file_url = None

    return render(request, 'portal/practicals/review_submission.html', {
        'submission': submission,
        'feedback_form': feedback_form,
        'file_url': file_url,  # Used by template viewer logic
    })
    

# ================= Certificate Management =================

# ================= Certificate Management =================

@login_required
def add_certificate(request, subject_id):
    """Teacher adds certificate template for a subject"""
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('home')
    
    subject = get_object_or_404(Subject, id=subject_id, teacher=request.user)

    if request.method == 'POST':
        if Certificate.objects.filter(subject=subject, teacher=request.user).exists():
            messages.warning(request, 'Certificate already added for this subject')
        else:
            # Create certificate template
            certificate = Certificate.objects.create(
                subject=subject,
                teacher=request.user,
                status='template_added'
            )
            
            # Handle file upload if provided
            if 'certificate_file' in request.FILES:
                certificate.file_path = request.FILES['certificate_file']
                certificate.save()
            
            # Create individual certificates for all students in this subject
            students = CustomUser.objects.filter(
                role='student',
                department=subject.department,
                student_class=subject.student_class
            )
            
            for student in students:
                # Create individual certificate for each student
                student_certificate = Certificate.objects.create(
                    student=student,
                    subject=subject,
                    teacher=request.user,
                    status='generated'
                )
                # Copy template file if available
                if certificate.file_path:
                    student_certificate.file_path = certificate.file_path
                    student_certificate.save()
            
            messages.success(request, f'Certificate template for {subject.name} added successfully ✅ Certificates generated for {students.count()} students.')
        return redirect('teacher_dashboard')

    return render(request, 'portal/certificates/teacher_add_certificate.html', {
        'subject': subject
    })

@login_required
def send_certificate(request, certificate_id):
    """Student sends certificate after completing all practicals"""
    if request.user.role != 'student':
        messages.error(request, 'Access denied')
        return redirect('home')

    certificate = get_object_or_404(Certificate, id=certificate_id)

    # Assign student if not already assigned
    if certificate.student is None:
        certificate.student = request.user
        certificate.save()

    # Check all practicals approved
    practicals = Practical.objects.filter(subject=certificate.subject)
    approved_count = PracticalSubmission.objects.filter(
        student=request.user,
        practical__subject=certificate.subject,
        status='approved'
    ).count()

    if approved_count < practicals.count():
        messages.error(request, 'Complete all practicals before sending certificate')
        return redirect('student_dashboard')

    # Update status if allowed
    if certificate.status in ['generated', 'template_added']:
        certificate.status = 'submitted_to_teacher'
        certificate.save()
        messages.success(request, 'Certificate sent to Teacher for approval ✅')
    else:
        messages.error(request, 'Certificate already processed')

    return redirect('student_dashboard')
@login_required
def submit_certificate(request, certificate_id):
    """Student uploads certificate file for a specific certificate"""
    if request.user.role != 'student':
        messages.error(request, 'Access denied')
        return redirect('home')

    certificate = get_object_or_404(Certificate, id=certificate_id)

    if request.method == 'POST':
        form = CertificateSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.student = request.user
            submission.status = 'pending'
            submission.save()
            messages.success(request, 'Certificate uploaded successfully ✅')
            return redirect('student_dashboard')
    else:
        form = CertificateSubmissionForm(initial={'certificate': certificate})

    return render(request, 'portal/certificates/add_certificate.html', {
        'form': form,
        'certificate': certificate
    })


@login_required
def approve_certificate_teacher(request, certificate_id):
    """
    Teacher approves a student's certificate and forwards it to the HOD.
    Only teachers can perform this action.
    """

    # ✅ Role check
    if not hasattr(request.user, 'role') or request.user.role.lower() != 'teacher':
        messages.error(request, 'Access denied ❌')
        return redirect('home')

    # ✅ Fetch certificate assigned to the current teacher
    certificate = get_object_or_404(Certificate, id=certificate_id, teacher=request.user)

    # ✅ Allow approval only if certificate is submitted or sent to teacher
    if certificate.status in ['submitted_to_teacher', 'sent_to_teacher']:
        certificate.status = 'sent_to_hod'
        certificate.approved_at = timezone.now()
        certificate.save()

        # ✅ Success message with student name
        student_name = certificate.student.username if certificate.student else "Unknown Student"
        messages.success(
            request,
            f'✅ Certificate for "{student_name}" has been approved and forwarded to HOD.'
        )
    else:
        # ⚠️ Warn if approval not allowed in current state
        messages.warning(
            request,
            f'⚠️ Certificate cannot be approved at this stage (Current status: {certificate.get_status_display()}).'
        )

    # ✅ Redirect teacher to their certificate dashboard
    return redirect('teacher_certificates')

@login_required
def teacher_certificates(request):
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('home')

    certificates = Certificate.objects.filter(teacher=request.user).order_by('-created_at')
    return render(request, 'portal/certificates/teacher_certificates.html', {
        'certificates': certificates
    })


@login_required
def approve_certificate_hod(request, certificate_id):
    """HOD certifies student certificate (final approval)"""
    if request.user.role != 'hod':
        messages.error(request, 'Access denied')
        return redirect('home')

    certificate = get_object_or_404(
        Certificate, 
        id=certificate_id, 
        subject__department=request.user.department,
        status='sent_to_hod'
    )

    certificate.status = 'sent_to_examiner'
    certificate.hod = request.user
    certificate.approved_at = timezone.now()
    certificate.save()

    messages.success(request, 'Certificate approved and sent to Examiner for final certification ✅')
    return redirect('hod_dashboard')
@login_required
def reject_certificate(request, certificate_id):
    """Teacher rejects a submitted certificate"""
    
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('home')

    certificate = get_object_or_404(Certificate, id=certificate_id, teacher=request.user)

    if certificate.status == 'submitted_to_teacher':
        certificate.status = 'rejected'
        certificate.save()
        messages.success(request, f'Certificate for {certificate.student.username} rejected ❌')
    else:
        messages.warning(request, f'Certificate cannot be rejected at this stage. Current status: {certificate.get_status_display()}')

    # Redirect to the teacher's certificate list page
    return redirect('teacher_certificates')



@login_required
def approve_certificate_teacher_ajax(request, certificate_id):
    """Teacher approves a student's certificate via AJAX"""
    if request.user.role != 'teacher':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)

    certificate = get_object_or_404(Certificate, id=certificate_id, teacher=request.user)

    if certificate.status == 'submitted_to_teacher':
        certificate.status = 'sent_to_hod'
        certificate.approved_at = timezone.now()
        certificate.save()
        return JsonResponse({'status': 'success', 'new_status': certificate.get_status_display()})
    else:
        return JsonResponse({'status': 'error', 'message': 'Cannot approve at this stage'}, status=400)


@login_required
def reject_certificate_ajax(request, certificate_id):
    """Teacher rejects a submitted certificate via AJAX"""
    if request.user.role != 'teacher':
        return JsonResponse({'status': 'error', 'message': 'Access denied'}, status=403)

    certificate = get_object_or_404(Certificate, id=certificate_id, teacher=request.user)

    if certificate.status == 'submitted_to_teacher':
        certificate.status = 'rejected'
        certificate.save()
        return JsonResponse({'status': 'success', 'new_status': certificate.get_status_display()})
    else:
        return JsonResponse({'status': 'error', 'message': 'Cannot reject at this stage'}, status=400)
@login_required
def toggle_exam_mode(request):
    if request.user.role != 'hod':
        messages.error(request, 'Access denied')
        return redirect('home')
    
    exam_mode, created = ExamMode.objects.get_or_create(
        department=request.user.department,
        defaults={'is_enabled': False}
    )
    
    if request.method == 'POST':
        form = ExamModeForm(request.POST, instance=exam_mode)
        if form.is_valid():
            form.save()
            status = 'enabled' if exam_mode.is_enabled else 'disabled'
            messages.success(request, f'Exam mode {status} for {exam_mode.get_department_display()}')
            return redirect('hod_dashboard')
    else:
        form = ExamModeForm(instance=exam_mode)
    
    return render(request, 'portal/exam_mode.html', {'form': form, 'exam_mode': exam_mode})

@login_required
def mark_best_practical(request, submission_id):
    if request.user.role != 'teacher':
        messages.error(request, 'Access denied')
        return redirect('home')
    
    submission = get_object_or_404(PracticalSubmission, id=submission_id, practical__teacher=request.user)
    
    if submission.status == 'approved':
        submission.practical.is_public = not submission.practical.is_public
        submission.practical.save()
        
        action = 'marked as best' if submission.practical.is_public else 'removed from best'
        messages.success(request, f'Practical {action} successfully')
    else:
        messages.error(request, 'Only approved practicals can be marked as best')
    
    return redirect('teacher_dashboard')

# Admin specific views
@login_required
def assign_hod_department(request, hod_id):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('home')
    
    hod = get_object_or_404(CustomUser, id=hod_id, role='hod')
    
    if request.method == 'POST':
        department = request.POST.get('department')
        if department in dict(CustomUser.DEPARTMENT_CHOICES):
            hod.department = department
            hod.save()
            messages.success(request, f'Department assigned to {hod.full_name}')
        else:
            messages.error(request, 'Invalid department selected')
        return redirect('admin_dashboard')
    
    return render(request, 'portal/admin/assign_department.html', {
        'hod': hod,
        'departments': CustomUser.DEPARTMENT_CHOICES
    })

@login_required
def create_examiner(request):
    if request.user.role != 'admin':
        messages.error(request, 'Access denied')
        return redirect('home')
    
    if request.method == 'POST':
        form = ExaminerCreationForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Examiner created successfully')
            return redirect('admin_dashboard')
    else:
        form = ExaminerCreationForm()
    
    return render(request, 'portal/admin/create_examiner.html', {'form': form})

# AJAX Views
@login_required
def get_subjects_by_department(request):
    department = request.GET.get('department')
    if department:
        subjects = Subject.objects.filter(department=department).values('id', 'name', 'code')
        subjects_list = list(subjects)
    else:
        subjects_list = []
    return JsonResponse({'subjects': subjects_list})
# File download views
@login_required
def download_submission(request, submission_id):
    submission = get_object_or_404(PracticalSubmission, id=submission_id)
    
    # Check permissions
    if (request.user.role == 'student' and submission.student != request.user) or \
       (request.user.role == 'teacher' and submission.practical.subject.teacher != request.user) or \
       (request.user.role == 'hod' and submission.practical.subject.department != request.user.department):
        messages.error(request, 'Access denied')
        return redirect('home')
    
    if not submission.file_path:
        raise Http404("File not found")
    
    try:
        # Check if file exists
        if not os.path.exists(submission.file_path.path):
            raise Http404("File not found on server")
        
        # Get file extension and set appropriate content type
        file_extension = get_file_extension(submission.file_path.name)
        
        content_type_map = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            
        }
        
        content_type = content_type_map.get(file_extension, 'application/octet-stream')
        
        # Read file in binary mode
        with open(submission.file_path.path, 'rb') as file:
            file_data = file.read()
        
        response = HttpResponse(file_data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(submission.file_path.name)}"'
        response['Content-Length'] = len(file_data)
        return response
        
    except Exception as e:
        messages.error(request, f'Error downloading file: {str(e)}')
        return redirect(request.META.get('HTTP_REFERER', 'home'))

@login_required
def download_certificate(request, certificate_id):
    certificate = get_object_or_404(Certificate, id=certificate_id)
    
    # Check permissions
    if (request.user.role == 'student' and certificate.student != request.user) or \
       (request.user.role == 'teacher' and certificate.teacher != request.user) or \
       (request.user.role == 'hod' and certificate.subject.department != request.user.department) or \
       (request.user.role == 'examiner' and certificate.subject.department != request.user.department):
        # Allow access for authorized users
        pass
    elif request.user.role not in ['admin']:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    if not certificate.file_path:
        raise Http404("Certificate file not found")
    
    try:
        # Check if file exists
        if not os.path.exists(certificate.file_path.path):
            raise Http404("Certificate file not found on server")
        
        # Get file extension and set appropriate content type
        file_extension = get_file_extension(certificate.file_path.name)
        
        content_type_map = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
            
        }
        
        content_type = content_type_map.get(file_extension, 'application/octet-stream')
        
        # Read file in binary mode
        with open(certificate.file_path.path, 'rb') as file:
            file_data = file.read()
        
        response = HttpResponse(file_data, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{os.path.basename(certificate.file_path.name)}"'
        response['Content-Length'] = len(file_data)
        return response
        
    except Exception as e:
        messages.error(request, f'Error downloading certificate: {str(e)}')
        return redirect(request.META.get('HTTP_REFERER', 'home'))
@login_required    
def approve_submission(request, submission_id):
    submission = get_object_or_404(PracticalSubmission, id=submission_id)
    submission.status = "approved"
    submission.save()
@login_required
def reject_submission(request, submission_id):
    submission = get_object_or_404(PracticalSubmission, id=submission_id)
    if request.user.role == 'teacher':   # ✅ फक्त teacher ला reject करु दे
        submission.status = 'rejected'
        submission.save()
        messages.success(request, "Submission rejected successfully.")
    else:
        messages.error(request, "You are not authorized to reject this submission.")
    return redirect('teacher_dashboard')

def login_selection(request):
    """Main login selection page"""
    return render(request, 'portal/login_selection.html')

@login_required
def student_certificates(request):
    """Show all certificates for logged-in student"""
    if request.user.role != 'student':
        messages.error(request, 'Access denied')
        return redirect('home')

    # Get subjects for this student
    subjects = Subject.objects.filter(
        department=request.user.department,
        student_class=request.user.student_class
    )
    
    # Certificates assigned to this student OR templates available for this student's subjects
    certificates = Certificate.objects.filter(
        student=request.user
    ) | Certificate.objects.filter(
        subject__in=subjects,
        student__isnull=True,
        status__in=[ 'submitted_to_teacher']
    )

    certificates = certificates.select_related('subject', 'teacher', 'hod').order_by('-created_at')

    return render(request, 'portal/certificates/student_certificates.html', {
        'certificates': certificates
    })

@login_required
def submit_certificate_form(request, certificate_id):
    """Student submits certificate file"""
    if request.user.role != 'student':
        messages.error(request, 'Access denied')
        return redirect('home')

    certificate = get_object_or_404(Certificate, id=certificate_id)

    # Check if student can submit this certificate
    if certificate.student and certificate.student != request.user:
        messages.error(request, 'Access denied')
        return redirect('student_dashboard')

    # Check practical completion
    practicals = Practical.objects.filter(subject=certificate.subject)
    approved_count = PracticalSubmission.objects.filter(
        student=request.user,
        practical__subject=certificate.subject,
        status='approved'
    ).count()

    if approved_count < practicals.count():
        messages.error(
            request,
            f'Complete all {practicals.count()} practicals before submitting certificate. You have completed {approved_count}.'
        )
        return redirect('student_dashboard')

    if request.method == 'POST':
        form = CertificateSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            # Assign student to certificate if needed
            if not certificate.student:
                existing_cert = Certificate.objects.filter(student=request.user, subject=certificate.subject).first()
                if existing_cert:
                    certificate = existing_cert
                else:
                    certificate.student = request.user
                    certificate.save()

            # Create new submission
            submission = form.save(commit=False)
            submission.student = request.user
            submission.certificate = certificate
            submission.status = 'pending'
            submission.submitted_at = timezone.now()
            submission.save()

            # Update certificate status
            certificate.status = 'submitted_to_teacher'
            certificate.submitted_at = timezone.now()
            certificate.save()

            messages.success(request, 'Certificate submitted successfully ✅')
            return redirect('student_dashboard')
        else:
            messages.error(request, 'There was a problem with your submission.')
    else:
        form = CertificateSubmissionForm()

    context = {
        'form': form,
        'certificate': certificate,
        'practicals_count': practicals.count(),
        'approved_count': approved_count,
    }
    return render(request, 'portal/certificates/submit_certificate_form.html', context)

# ================= Google Docs Viewer =================

@login_required
def view_practical_submission(request, submission_id):
    """View practical submission using Google Docs viewer"""
    submission = get_object_or_404(PracticalSubmission, id=submission_id)
    
    # Check permissions
    if request.user.role == 'student' and submission.student != request.user:
        messages.error(request, 'Access denied')
        return redirect('student_dashboard')
    elif request.user.role == 'teacher' and submission.practical.subject.teacher != request.user:
        messages.error(request, 'Access denied')
        return redirect('teacher_dashboard')
    elif request.user.role == 'hod' and submission.practical.subject.department != request.user.department:
        messages.error(request, 'Access denied')
        return redirect('hod_dashboard')
    
    if not submission.file_path:
        messages.error(request, 'No file available for preview')
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    # Get file URL
    try:
        # Use direct media URL instead of build_absolute_uri
        file_url = f"{request.scheme}://{request.get_host()}{submission.file_path.url}"
        google_viewer_url = get_google_docs_viewer_url(file_url)
        
        # Debug info
        print(f"File URL: {file_url}")
        print(f"Google Viewer URL: {google_viewer_url}")
        
    except Exception as e:
        messages.error(request, f'Error generating file URL: {str(e)}')
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    context = {
        'google_viewer_url': google_viewer_url,
        'file_url': file_url,
        'file_id': submission_id,
        'document_title': f"Practical Submission - {submission.practical.title}",
        'file_name': os.path.basename(submission.file_path.name),
        'file_type': get_file_extension(submission.file_path.name).upper().replace('.', ''),
        'file_icon': get_file_icon(submission.file_path.name),
        'file_info': True,
        'student_name': submission.student.full_name,
        'subject_name': f"{submission.practical.subject.code} - {submission.practical.subject.name}",
    }
    
    return render(request, 'portal/viewer/google_docs_viewer.html', context)

@login_required
def view_certificate(request, certificate_id):
    """View certificate using Google Docs viewer"""
    certificate = get_object_or_404(CertificateSubmission, id=certificate_id)
    
    # Check permissions
    if request.user.role == 'student' and certificate.student != request.user:
        messages.error(request, 'Access denied')
        return redirect('student_dashboard')
    elif request.user.role == 'teacher' and certificate.certificate.subject.teacher != request.user:
        messages.error(request, 'Access denied')
        return redirect('teacher_dashboard')
    elif request.user.role == 'hod' and certificate.subject.department != request.user.department:
        messages.error(request, 'Access denied')
        return redirect('hod_dashboard')
    
    if not certificate.file_path:
        messages.error(request, 'No certificate file available for preview')
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    # Get file URL
    try:
        # Use direct media URL instead of build_absolute_uri
        file_url = f"{request.scheme}://{request.get_host()}{certificate.file_path.url}"
        google_viewer_url = get_google_docs_viewer_url(file_url)
        
        # Debug info
        print(f"Certificate File URL: {file_url}")
        print(f"Certificate Google Viewer URL: {google_viewer_url}")
        
    except Exception as e:
        messages.error(request, f'Error generating certificate URL: {str(e)}')
        return redirect(request.META.get('HTTP_REFERER', 'home'))
    
    context = {
        'google_viewer_url': google_viewer_url,
        'file_url': file_url,
        'file_id': certificate_id,
        'document_title': f"Certificate - {certificate.certificate.subject.name}",
        'file_name': os.path.basename(certificate.file_path.name),
        'file_type': get_file_extension(certificate.file_path.name).upper().replace('.', ''),
        'file_icon': get_file_icon(certificate.file_path.name),
        'file_info': True,
        'student_name': certificate.student.full_name if certificate.student else 'N/A',
        'subject_name': f"{certificate.certificate.subject.code} - {certificate.certificate.subject.name}",
    }
    
    return render(request, 'portal/viewer/google_docs_viewer.html', context)

# ================= Examiner Certificate Management =================

@login_required
def examiner_certificates(request):
    """Show certificates pending examiner approval"""
    if request.user.role != 'examiner':
        messages.error(request, 'Access denied')
        return redirect('home')

    certificates = Certificate.objects.filter(
        status='sent_to_examiner',
        subject__department=request.user.department
    ).select_related('student', 'subject', 'teacher', 'hod').order_by('-created_at')

    return render(request, 'portal/certificates/examiner_certificates.html', {
        'certificates': certificates
    })

@login_required
def approve_certificate_examiner(request, certificate_id):
    """Examiner approves certificate and sends to final certification"""
    if request.user.role != 'examiner':
        messages.error(request, 'Access denied')
        return redirect('home')

    certificate = get_object_or_404(
        Certificate, 
        id=certificate_id, 
        subject__department=request.user.department,
        status='sent_to_examiner'
    )

    certificate.status = 'certified'
    certificate.examiner = request.user
    certificate.examiner_approved_at = timezone.now()
    certificate.certified_at = timezone.now()
    certificate.save()

    messages.success(request, f'Certificate for {certificate.student.full_name} certified successfully ✅')
    return redirect('examiner_certificates')

@login_required
def reject_certificate_examiner(request, certificate_id):
    """Examiner rejects certificate"""
    if request.user.role != 'examiner':
        messages.error(request, 'Access denied')
        return redirect('home')

    certificate = get_object_or_404(
        Certificate, 
        id=certificate_id, 
        subject__department=request.user.department,
        status='sent_to_examiner'
    )

    certificate.status = 'rejected'
    certificate.examiner = request.user
    certificate.save()

    messages.success(request, f'Certificate for {certificate.student.full_name} rejected ❌')
    return redirect('examiner_certificates')

# ================= File Test View =================

@login_required
def test_file_access(request):
    """Test view to check file accessibility"""
    if request.user.role not in ['admin', 'teacher']:
        messages.error(request, 'Access denied')
        return redirect('home')
    
    # Get a sample file to test
    submissions = PracticalSubmission.objects.filter(file_path__isnull=False)[:5]
    certificates = Certificate.objects.filter(file_path__isnull=False)[:5]
    
    context = {
        'submissions': submissions,
        'certificates': certificates,
    }
    
    return render(request, 'portal/test_file_access.html', context)

# ================= Direct File Serving =================

@login_required
def serve_file_direct(request, file_type, file_id):
    """Direct file serving without Google Docs viewer"""
    if file_type == 'submission':
        obj = get_object_or_404(PracticalSubmission, id=file_id)
        # Check permissions
        if (request.user.role == 'student' and obj.student != request.user) or \
           (request.user.role == 'teacher' and obj.practical.subject.teacher != request.user) or \
           (request.user.role == 'hod' and obj.practical.subject.department != request.user.department):
            messages.error(request, 'Access denied')
            return redirect('home')
    elif file_type == 'certificate':
        obj = get_object_or_404(Certificate, id=file_id)
        # Check permissions
        if (request.user.role == 'student' and obj.student != request.user) or \
           (request.user.role == 'teacher' and obj.teacher != request.user) or \
           (request.user.role == 'hod' and obj.subject.department != request.user.department) or \
           (request.user.role == 'examiner' and obj.subject.department != request.user.department):
            pass
        elif request.user.role not in ['admin']:
            messages.error(request, 'Access denied')
            return redirect('home')
    else:
        raise Http404("Invalid file type")
    
    if not obj.file_path:
        raise Http404("File not found")
    
    try:
        # Check if file exists
        if not os.path.exists(obj.file_path.path):
            raise Http404("File not found on server")
        
        # Get file extension and set appropriate content type
        file_extension = get_file_extension(obj.file_path.name)
        
        content_type_map = {
            '.pdf': 'application/pdf',
            '.doc': 'application/msword',
            '.docx': 'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
          
        }
        
        content_type = content_type_map.get(file_extension, 'application/octet-stream')
        
        # Read file in binary mode
        with open(obj.file_path.path, 'rb') as file:
            file_data = file.read()
        
        response = HttpResponse(file_data, content_type=content_type)
        response['Content-Disposition'] = f'inline; filename="{os.path.basename(obj.file_path.name)}"'
        response['Content-Length'] = len(file_data)
        return response
        
    except Exception as e:
        messages.error(request, f'Error serving file: {str(e)}')
        return redirect(request.META.get('HTTP_REFERER', 'home'))

from .forms import HODStudentUpdateForm,UserPasswordUpdateForm
from django.contrib.auth import update_session_auth_hash

@login_required
def update_password(request):
    if request.method == "POST":
        form = UserPasswordUpdateForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Password updated successfully!")
            return redirect('dashboard')
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = UserPasswordUpdateForm(request.user)

    return render(request, 'portal/update_password.html', {'form': form})


from .forms import HODStudentUpdateForm

@login_required
def hod_update_student(request, student_id):
    user = request.user
    if user.role != 'hod':
        return redirect('no_permission')

    student = CustomUser.objects.get(id=student_id, role='student')

    if request.method == "POST":
        form = HODStudentUpdateForm(request.POST, instance=student)
        if form.is_valid():
            form.save()
            messages.success(request, "Student profile updated successfully!")
            return redirect('hod_dashboard')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        form = HODStudentUpdateForm(instance=student)

    return render(request, 'portal/hod_update_student.html', {'form': form, 'student': student})







@login_required
def hod_delete_student(request, id):

    if request.user.role != "hod":
        return redirect("home")

    student = get_object_or_404(CustomUser, id=id, role="student")
    student.delete()

    return redirect("hod_dashboard")


# HOD Subject List
@login_required
def hod_subject_list(request):
    if request.user.role != 'hod':
        return redirect('home')
    
    subjects = Subject.objects.all()
    teachers = CustomUser.objects.filter(role='teacher')
    
    return render(request, 'portal/hod_subject_list.html', {'subjects': subjects, 'teachers': teachers})

# Renew Practicals + Assign Teacher
@login_required
def renew_practicals(request, subject_id):
    if request.user.role != 'hod':
        return redirect('home')

    subject = get_object_or_404(
        Subject,
        id=subject_id,
        department=request.user.department
    )

    if request.method == 'POST':

        # 1) DELETE Certificate Submissions FIRST (child table)
        CertificateSubmission.objects.filter(
            certificate__subject=subject
        ).delete()

        # 2) DELETE Certificates
        Certificate.objects.filter(
            subject=subject
        ).delete()

        # 3) DELETE Practicals for this subject
        Practical.objects.filter(
            subject=subject
        ).delete()

        # 4) Assign NEW teacher if selected
        teacher_id = request.POST.get('teacher_id')
        if teacher_id:
            teacher = get_object_or_404(
                CustomUser,
                id=teacher_id,
                role='teacher',
                department=request.user.department
            )
            subject.teacher = teacher
            subject.save()

        messages.success(
            request,
            f"All Practicals and Certificates for {subject.name} have been deleted and renewed successfully."
        )
        return redirect('hod_dashboard')

    return redirect('hod_subject_list')
