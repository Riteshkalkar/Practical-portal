from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError


# Custom User Manager
class CustomUserManager(BaseUserManager):
    def create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("Email is required")
        if not extra_fields.get("full_name"):
            raise ValueError("Full name is required")
        if not extra_fields.get("role"):
            raise ValueError("Role is required")

        email = self.normalize_email(email)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("full_name", "Administrator")
        extra_fields.setdefault("role", "admin")
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        return self.create_user(username, email, password, **extra_fields)


# Custom User Model
class CustomUser(AbstractUser):
    ROLE_CHOICES = [
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('hod', 'HOD'),
        ('admin', 'Admin'),
        ('examiner', 'Examiner'),
    ]

    DEPARTMENT_CHOICES = [
        ('computer_science', 'Computer Science'),
    ]

    CLASS_CHOICES = [
        ('Semester 1', 'Semester 1'),
        ('Semester 2', 'Semester 2'),
        ('Semester 3', 'Semester 3'),
        ('Semester 4', 'Semester 4'),
        ('Semester 5', 'Semester 5'),
        ('Semester 6', 'Semester 6'),
        
    ]

    full_name = models.CharField(max_length=200)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    department = models.CharField(max_length=50, choices=DEPARTMENT_CHOICES, blank=True, null=True)
    student_class = models.CharField(max_length=20, choices=CLASS_CHOICES, blank=True, null=True)
    roll_number = models.CharField(max_length=20, blank=True, null=True)  # Remove unique=True

    objects = CustomUserManager()

    def clean(self):
        if self.role == 'student':
            if not self.roll_number:
                raise ValidationError({'roll_number': 'Roll number is required for students'})
            if not self.student_class:
                raise ValidationError({'student_class': 'Class is required for students'})
            
            # Check unique roll number within the same class
            if CustomUser.objects.filter(
                roll_number=self.roll_number,
                student_class=self.student_class,
                role='student'
            ).exclude(pk=self.pk).exists():
                raise ValidationError({'roll_number': 'This roll number is already taken in this class'})

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.username} ({self.role})"

# Subject Model
class Subject(models.Model):
    name = models.CharField(max_length=200)
    code = models.CharField(max_length=20, unique=True)
    department = models.CharField(max_length=50, choices=CustomUser.DEPARTMENT_CHOICES)
    student_class = models.CharField(max_length=20, choices=CustomUser.CLASS_CHOICES)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.code} - {self.name}"


# Practical Model
class Practical(models.Model):
    number = models.IntegerField()
    title = models.CharField(max_length=200)
    description = models.TextField()
    deadline = models.DateTimeField()
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE)
    teacher = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'teacher'})
    is_public = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['number', 'subject']

    def __str__(self):
        return f"Practical {self.number}: {self.title}"


# Practical Submission Model
class PracticalSubmission(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('submitted', 'Submitted'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(CustomUser, on_delete=models.CASCADE, limit_choices_to={'role': 'student'})
    practical = models.ForeignKey(Practical, on_delete=models.CASCADE)

    file_path = models.FileField(upload_to='practicals/', blank=True, null=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    is_draft = models.BooleanField(default=True)
    is_late = models.BooleanField(default=False)
    feedback = models.TextField(blank=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_public = models.BooleanField(default=False)
    class Meta:
        unique_together = ['student', 'practical']

    def save(self, *args, **kwargs):
        if not self.is_draft and not self.submitted_at:
            self.submitted_at = timezone.now()
            if self.submitted_at > self.practical.deadline:
                self.is_late = True
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.practical.title}"


# Certificate Model

class Certificate(models.Model):
    STATUS_CHOICES = [
       
        ('submitted_to_teacher', 'Submitted to Teacher'),
        ('sent_to_hod', 'Sent to HOD'),
        ('sent_to_examiner', 'Sent to Examiner'),
        ('certified', 'Certified'),
        ('rejected', 'Rejected'),
    ]

    student = models.ForeignKey(
        'CustomUser', 
        on_delete=models.CASCADE, 
        limit_choices_to={'role': 'student'},
        blank=True,   # optional for template creation
        null=True     # optional for template creation
    )
    subject = models.ForeignKey('Subject', on_delete=models.CASCADE)

    teacher = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'teacher'},
        related_name='teacher_certificates'
    )
    hod = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'hod'},
        blank=True,
        null=True,
        related_name='hod_certificates'
    )
    examiner = models.ForeignKey(
        'CustomUser',
        on_delete=models.CASCADE,
        limit_choices_to={'role': 'examiner'},
        blank=True,
        null=True,
        related_name='examiner_certificates'
    )

    file_path = models.FileField(upload_to='certificates/', blank=True, null=True)
    status = models.CharField(max_length=30, choices=STATUS_CHOICES, default='draft')
    teacher_feedback = models.TextField(blank=True, null=True)
    hod_feedback = models.TextField(blank=True, null=True)
    examiner_feedback = models.TextField(blank=True, null=True)

    created_at = models.DateTimeField(auto_now_add=True)
    submitted_at = models.DateTimeField(blank=True, null=True)
    approved_at = models.DateTimeField(blank=True, null=True)
    examiner_approved_at = models.DateTimeField(blank=True, null=True)
    certified_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ['student', 'subject']

    def save(self, *args, **kwargs):
        # Student can submit only if all practicals approved
        if self.status == 'submitted_to_teacher' and self.student:
            all_practicals = Practical.objects.filter(subject=self.subject)
            approved_count = PracticalSubmission.objects.filter(
                student=self.student,
                practical__in=all_practicals,
                status='approved'
            ).count()

            if approved_count < all_practicals.count():
                raise ValidationError("All practicals must be approved before submitting the certificate.")

            if not self.submitted_at:
                self.submitted_at = timezone.now()

        if self.status == 'sent_to_hod' and not self.approved_at:
            self.approved_at = timezone.now()

        if self.status == 'sent_to_examiner' and not self.examiner_approved_at:
            self.examiner_approved_at = timezone.now()

        if self.status == 'certified' and not self.certified_at:
            self.certified_at = timezone.now()

        super().save(*args, **kwargs)

    def __str__(self):
        student_name = self.student.username if self.student else "N/A"
        subject_name = self.subject.name if self.subject else "N/A"
        return f"Certificate - {student_name} - {subject_name} ({self.status})"



class CertificateSubmission(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('sent_to_hod', 'Sent to HOD'),
        ('certified', 'Certified'),
        ('rejected', 'Rejected'),
    ]

    certificate = models.ForeignKey('Certificate', on_delete=models.CASCADE)
    student = models.ForeignKey('CustomUser', on_delete=models.CASCADE)
    file_path = models.FileField(upload_to='certificates/')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(default=timezone.now)
    teacher_feedback = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.student.full_name} - {self.certificate.title}"


# Exam Mode Model
class ExamMode(models.Model):
    department = models.CharField(max_length=50, choices=CustomUser.DEPARTMENT_CHOICES, unique=True)
    is_enabled = models.BooleanField(default=False)
    enabled_at = models.DateTimeField(blank=True, null=True)

    def save(self, *args, **kwargs):
        if self.is_enabled and not self.enabled_at:
            self.enabled_at = timezone.now()
        elif not self.is_enabled:
            self.enabled_at = None
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.department} - {'Enabled' if self.is_enabled else 'Disabled'}"
