from django.urls import path
from . import views
from portal.views import update_password,hod_update_student

urlpatterns = [
    # Home
    path('', views.home, name='home'),
    
    # Authentication
    path('login/student/', views.student_login, name='student_login'),
    path('login/teacher/', views.teacher_login, name='teacher_login'),
    path('login/hod/', views.hod_login, name='hod_login'),
    path('login/admin/', views.admin_login, name='admin_login'),
    path('login/examiner/', views.examiner_login, name='examiner_login'),
    path('register/student/', views.student_register, name='student_register'),
    path('register/teacher/', views.teacher_register, name='teacher_register'),
    path('register/hod/', views.hod_register, name='hod_register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('dashboard/student/', views.student_dashboard, name='student_dashboard'),
    path('dashboard/teacher/', views.teacher_dashboard, name='teacher_dashboard'),
    path('dashboard/hod/', views.hod_dashboard, name='hod_dashboard'),
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/examiner/', views.examiner_dashboard, name='examiner_dashboard'),
    
    # Subject Management
    path('subjects/add/', views.add_subject, name='add_subject'),
    
    # Practical Management
    path('subjects/<int:subject_id>/add-practical/', views.add_practical, name='add_practical'),
    path('practicals/<int:practical_id>/', views.practical_detail, name='practical_detail'),
    path('practicals/<int:practical_id>/submit/', views.submit_practical, name='submit_practical'),
    path('submissions/<int:submission_id>/review/', views.review_submission, name='review_submission'),
    path('submissions/<int:submission_id>/mark-best/', views.mark_best_practical, name='mark_best_practical'),
    path('approve_submission/<int:submission_id>/', views.approve_submission, name='approve_submission'),
    path('submission/<int:submission_id>/reject/', views.reject_submission, name='reject_submission'),


    path('certificate/add/', views.add_certificate, name='add_certificate'),
    path('certificate/send/<int:certificate_id>/', views.send_certificate, name='send_certificate'),
    path('certificate/approve/teacher/<int:certificate_id>/', views.approve_certificate_teacher, name='approve_certificate_teacher'),
    path('certificate/approve/hod/<int:certificate_id>/', views.approve_certificate_hod, name='approve_certificate_hod'),
    path('certificate/submit/<int:certificate_id>/', views.submit_certificate, name='submit_certificate'),
    path('student/certificates/', views.student_certificates, name='student_certificates'),
    path('certificate/reject/<int:certificate_id>/', views.reject_certificate, name='reject_certificate'),
    path('teacher/certificates/', views.teacher_certificates, name='teacher_certificates'),

    # Exam Mode
    path('exam-mode/toggle/', views.toggle_exam_mode, name='toggle_exam_mode'),
    
    # Admin Functions
    path('admin/hod/<int:hod_id>/assign-department/', views.assign_hod_department, name='assign_hod_department'),
    path('admin/create-examiner/', views.create_examiner, name='create_examiner'),
    path('assign-hod-department/<int:hod_id>/', views.assign_hod_department, name='assign_hod_department'),
    # AJAX
    path('ajax/subjects-by-department/', views.get_subjects_by_department, name='get_subjects_by_department'),
    
    # Downloads
    path('submissions/<int:submission_id>/download/', views.download_submission, name='download_submission'),
    path('teacher/add-certificate/<int:subject_id>/', views.add_certificate, name='add_certificate'),
    path('teacher/approve-certificate/<int:certificate_id>/', views.approve_certificate_teacher, name='approve_certificate_teacher'),

    # Student routes
    path('student/send-certificate/<int:certificate_id>/', views.send_certificate, name='send_certificate'),
    path('student/submit-certificate/<int:certificate_id>/', views.submit_certificate_form, name='submit_certificate_form'),

    # HOD routes
    path('hod/approve-certificate/<int:certificate_id>/', views.approve_certificate_hod, name='approve_certificate_hod'),
    path('hod/certify-certificate/<int:certificate_id>/', views.approve_certificate_hod, name='certify_certificate'),
    path('login-selection/', views.login_selection, name='login_selection'),
    
    # Google Docs Viewer URLs
    path('view/practical/<int:submission_id>/', views.view_practical_submission, name='view_practical_submission'),
    path('view/certificate/<int:certificate_id>/', views.view_certificate, name='view_certificate'),
    
    # Direct File Serving URLs
    path('file/<str:file_type>/<int:file_id>/', views.serve_file_direct, name='serve_file_direct'),
    
    # Test URLs
    path('test/files/', views.test_file_access, name='test_file_access'),
    
    # Examiner routes
    path('examiner/certificates/', views.examiner_certificates, name='examiner_certificates'),
    path('examiner/approve-certificate/<int:certificate_id>/', views.approve_certificate_examiner, name='approve_certificate_examiner'),
    path('examiner/reject-certificate/<int:certificate_id>/', views.reject_certificate_examiner, name='reject_certificate_examiner'),
    
    # Download URLs
    path('certificate/download/<int:certificate_id>/', views.download_certificate, name='download_certificate'),
    path('profile/change-password/', update_password, name='update_password'),
    path('hod/student/<int:student_id>/edit/', hod_update_student, name='hod_update_student'),
    path('hod/student/delete/<int:id>/', views.hod_delete_student, name='hod_delete_student'),
    path('hod/subjects/', views.hod_subject_list, name='hod_subject_list'),
    path('hod/subjects/renew/<int:subject_id>/', views.renew_practicals, name='renew_practicals'),
]