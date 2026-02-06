from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate
from tinymce.widgets import TinyMCE
from .models import CustomUser, Subject, Practical, PracticalSubmission, ExamMode,CertificateSubmission


class StudentRegistrationForm(UserCreationForm):
    full_name = forms.CharField(
        max_length=200, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control'})
    )
    department = forms.ChoiceField(
        choices=CustomUser.DEPARTMENT_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    student_class = forms.ChoiceField(
        choices=CustomUser.CLASS_CHOICES, 
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    roll_number = forms.CharField(
        max_length=20, 
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'full_name', 'email', 
            'department', 'student_class', 'roll_number', 
            'password1', 'password2'
        ]
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['department', 'student_class']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
    
   
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'student'
        user.full_name = self.cleaned_data['full_name']
        user.department = self.cleaned_data['department']
        user.student_class = self.cleaned_data['student_class']
        user.roll_number = self.cleaned_data['roll_number']

      
        user.set_password(self.cleaned_data['password1'])

        if commit:
            user.save() 
        return user



class TeacherRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    department = forms.ChoiceField(choices=CustomUser.DEPARTMENT_CHOICES, widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = CustomUser
        fields = ['username', 'full_name', 'email', 'department',  'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field not in ['department', 'signature']:
                self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'teacher'
        if commit:
            user.save()
        return user


class HODRegistrationForm(UserCreationForm):
    full_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    
    class Meta:
        model = CustomUser
        fields = ['username', 'full_name', 'email',  'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            if field != 'signature':
                self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'hod'
        if commit:
            user.save()
        return user

class ExaminerCreationForm(UserCreationForm):
    full_name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    class Meta:
        model = CustomUser
        fields = ['username', 'full_name', 'email', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({'class': 'form-control'})
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.role = 'examiner'
        if commit:
            user.save()
        return user


class CustomLoginForm(forms.Form):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={
            'class': 'form-control form-control-lg shadow-sm',
            'placeholder': 'Enter your username',
        })
    )
    password = forms.CharField(
        label="Password",
        widget=forms.PasswordInput(attrs={
            'class': 'form-control form-control-lg shadow-sm',
            'placeholder': 'Enter your password',
        })
    )

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        self.role = kwargs.pop('role', None)
        self.user = None
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')

        if username and password:
            user = authenticate(self.request, username=username, password=password)
            if not user:
                raise forms.ValidationError("Invalid username or password")
            if self.role and user.role != self.role:
                raise forms.ValidationError(f"You don't have {self.role} access")
            self.user = user
        return cleaned_data


class SubjectForm(forms.ModelForm):
    class Meta:
        model = Subject
        fields = ['name', 'code', 'department', 'student_class', 'teacher']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'code': forms.TextInput(attrs={'class': 'form-control'}),
            'department': forms.Select(attrs={'class': 'form-select'}),
            'student_class': forms.Select(attrs={'class': 'form-select'}),
            'teacher': forms.Select(attrs={'class': 'form-select'}),
        }

class PracticalForm(forms.ModelForm):
    class Meta:
        model = Practical
        fields = ['number', 'title', 'description', 'deadline']
        widgets = {
            'number': forms.NumberInput(attrs={'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'deadline': forms.DateTimeInput(attrs={'class': 'form-control', 'type': 'datetime-local'}),
        }


class PracticalSubmissionForm(forms.ModelForm):
    class Meta:
        model = PracticalSubmission
        fields = ['file_path']
        widgets = {
            'content': TinyMCE(attrs={'class': 'form-control'}),
            'file_path': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }


class FeedbackForm(forms.Form):
    feedback = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        required=False
    )


class ExamModeForm(forms.ModelForm):
    class Meta:
        model = ExamMode
        fields = ['is_enabled']
        widgets = {
            'is_enabled': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


from django import forms
from .models import CustomUser, Subject

from django import forms
from .models import CustomUser, Subject

class ExaminerSearchForm(forms.Form):
    department = forms.ChoiceField(
        choices=CustomUser.DEPARTMENT_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    student_class = forms.ChoiceField(
        choices=CustomUser.CLASS_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=True
    )
    roll_number = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control'}),
        required=True
    )
    subject = forms.ModelChoiceField(
        queryset=Subject.objects.all(),
        widget=forms.Select(attrs={'class': 'form-select'}),
        required=False,
        empty_label="All Subjects"
    )

class CertificateSubmissionForm(forms.ModelForm):
    class Meta:
        model = CertificateSubmission
        fields = ['file_path']



class HODStudentUpdateForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = ['student_class', 'roll_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['student_class'].widget.attrs.update({'class': 'form-select'})
        self.fields['roll_number'].widget.attrs.update({'class': 'form-control'})

from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User

class UserPasswordUpdateForm(PasswordChangeForm):
    def __init__(self, *args, **kwargs):
        super(UserPasswordUpdateForm, self).__init__(*args, **kwargs)

        # Add Bootstrap classes to all fields
        for field in self.fields.values():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
            })

    class Meta:
        model = User
        fields = ['old_password', 'new_password1', 'new_password2']
