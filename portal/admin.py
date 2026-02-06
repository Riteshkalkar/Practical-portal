from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.urls import path
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import CustomUser, Subject, Practical, PracticalSubmission, Certificate, ExamMode

# CustomUser Admin
@admin.register(CustomUser)
class CustomUserAdmin(UserAdmin):
    model = CustomUser
    list_display = ['username', 'email', 'full_name', 'role', 'department', 'student_class', 'roll_number', 'is_staff']
    list_filter = ['role', 'department', 'student_class']

    fieldsets = UserAdmin.fieldsets + (
        ('Custom Fields', {
            'fields': ('full_name', 'role', 'department', 'student_class', 'roll_number', 'signature')
        }),
    )

    add_fieldsets = UserAdmin.add_fieldsets + (
        ('Custom Fields', {
            'fields': ('full_name', 'role', 'department', 'student_class', 'roll_number', 'signature')
        }),
    )

    list_editable = ['department']

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs

    # Custom URL for creating examiner
    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'create-examiner/',
                self.admin_site.admin_view(self.create_examiner_view),
                name='create-examiner'
            ),
        ]
        return custom_urls + urls

    # Custom view function
    def create_examiner_view(self, request):
        if request.method == 'POST':
            username = request.POST.get('username')
            email = request.POST.get('email')
            full_name = request.POST.get('full_name')
            password = request.POST.get('password')

            if username and email and password:
                CustomUser.objects.create_user(
                    username=username,
                    email=email,
                    full_name=full_name,
                    password=password,
                    role='examiner',  # role automatically examiner set hoil
                )
                messages.success(request, f'Examiner {username} created successfully!')
                return redirect('admin:portal_customuser_changelist')
            else:
                messages.error(request, 'Please fill all fields!')

        return render(request, 'portal/admin/create_examiner.html')


# Subject Admin
@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'department', 'student_class', 'teacher']
    list_filter = ['department', 'student_class']
    search_fields = ['name', 'code']


# Practical Admin
@admin.register(Practical)
class PracticalAdmin(admin.ModelAdmin):
    list_display = ['number', 'title', 'subject', 'teacher', 'deadline']
    list_filter = ['subject', 'teacher']
    search_fields = ['title', 'description']


# PracticalSubmission Admin
@admin.register(PracticalSubmission)
class PracticalSubmissionAdmin(admin.ModelAdmin):
    list_display = ['student', 'practical', 'status', 'is_draft', 'is_late', 'submitted_at']
    list_filter = ['status', 'is_draft', 'is_late']
    search_fields = ['student__username', 'practical__title']


# Certificate Admin
@admin.register(Certificate)
class CertificateAdmin(admin.ModelAdmin):
    list_display = ['student', 'subject', 'teacher', 'hod', 'status', 'created_at']
    list_filter = ['status', 'subject']
    search_fields = ['student__username', 'subject__name']


# ExamMode Admin
@admin.register(ExamMode)
class ExamModeAdmin(admin.ModelAdmin):
    list_display = ['department', 'is_enabled']
    list_filter = ['is_enabled']
