# 📌 Practical Submission Portal

## 📖 Description
The **Practical Submission Portal** is a web-based application designed to digitize the traditional manual practical submission process. Students no longer need to print and submit practical files physically. Teachers, HODs, and examiners can efficiently manage, review, approve, and track submissions online. This system improves workflow efficiency and helps in **reducing paper wastage**.

---

## 👥 Users & Roles

- **Admin**
  - Create HODs and assign departments  
  - Create Examiners and assign departments  
  - Full system control  

- **HOD**
  - Create Teachers  
  - Create Subjects and assign teachers  
  - Manage students  
  - Approve student certificates  
  - Enable/Disable Exam Mode  

- **Teacher**
  - Create practicals for assigned subjects  
  - View, approve, or reject student submissions with remarks  
  - Upload and approve certificates  

- **Examiner**
  - View submissions of assigned departments  
  - Final approval of certificates  

- **Student**
  - Register and login  
  - View assigned practicals  
  - Upload practical files and certificates  
  - Track submission and approval status  

---

## 🚀 Features
- Role-based access control  
- Practical upload and approval system  
- Certificate upload and verification  
- Submission status tracking  
- Exam Mode to restrict access during examinations  
- Password update functionality for all roles  

---

## 🛠️ Tech Stack
- **Frontend:** HTML, CSS, JavaScript, Bootstrap  
- **Backend:** Django  
- **Database:** MySQL  
- **Authentication:** Django Authentication System  
- **File Storage:** Local Server  

---

## 📂 Project Structure

```
ADVANCE PRACTICAL PORTAL/
│
├── media/
│   ├── certificates/        # Uploaded/generated certificates
│   └── practicals/          # Uploaded practical files
│
├── portal/                  # Main Django app
│   ├── _pycache_/
│   ├── migrations/          # Database migrations
│   ├── templatetags/        # Custom template filters/tags
│   ├── _init_.py
│   ├── admin.py             # Django admin configurations
│   ├── apps.py              # App configuration
│   ├── forms.py             # Django forms
│   ├── models.py            # Database models
│   ├── urls.py              # App-level URL routing
│   ├── utils.py             # Utility/helper functions
│   └── views.py             # Application views (business logic)
│
├── practical_portal/        # Django project settings
│   ├── _pycache_/
│   ├── _init_.py
│   ├── settings.py          # Global project settings
│   ├── urls.py              # Root URL configuration
│   └── wsgi.py              # WSGI configuration
│
├── static/                  # Static assets
│   ├── css/                 # Stylesheets
│   ├── docxjs/              # DOCX viewer scripts
│   ├── images/              # Images/icons
│   ├── pdfjs/               # PDF viewer scripts
│   └── viewer/              # File viewer assets
│
├── templates/               # HTML templates
│   └── portal/
│       ├── admin/           # Admin templates
│       ├── auth/            # Authentication pages
│       ├── certificates/    # Certificate-related pages
│       ├── dashboards/      # Dashboards for roles
│       ├── practicals/      # Practical submission/view pages
│       ├── subjects/        # Subject management pages
│       ├── viewer/          # File viewing pages
│       ├── exam_mode.html
│       ├── hod_student_list.html
│       ├── hod_subject_list.html
│       ├── hod_update_student.html
│       ├── home.html
│       ├── login_selection.html
│       ├── test_file_access.html
│       ├── update_password.html
│       └── base.html        # Base layout template
│
├── venv/                    # Python virtual environment
├── manage.py                # Django management script
├── README.md                # Project documentation
└── requirements.txt         # Project dependencies
```

---

## ⚙️ Installation & Setup

### 1️⃣ Clone Repository & Create Virtual Environment
```bash
git clone https://github.com/Riteshkalkar/Practical-Portal.git
cd practical-portal
python -m venv venv
source venv/bin/activate   # Windows: venv\Scripts\activate
```

### 2️⃣ Install Dependencies
```bash
pip install -r requirements.txt
```

### 3️⃣ Database Migration
```bash
python manage.py makemigrations
python manage.py migrate
```

### 4️⃣ Create Admin User
```bash
python manage.py createsuperuser
```

### 5️⃣ Run Server
```bash
python manage.py runserver
```

### 6️⃣ Access Application
```
http://127.0.0.1:8000/
```

---

## 📘 Usage Guide

- **Admin:** Creates HODs and Examiners, assigns departments  
- **HOD:** Creates subjects, assigns teachers, manages students, controls exam mode  
- **Teacher:** Creates practicals, reviews submissions, generates certificates  
- **Student:** Uploads practicals and certificates, tracks status  
- **Examiner:** Views submissions and gives final certificate approval  

---

## 📝 Certificate Approval Flow

```
Student completes practicals
        ↓
Teacher approves certificate
        ↓
HOD approval
        ↓
Examiner final approval
```

---

## 🔮 Future Enhancements
- Cloud storage integration for scalable file management  
- Email notifications for students, teachers, and examiners  

---

## 🤝 Contributing
Contributions are welcome.  
Feel free to fork this repository and submit a pull request.

---

## 📄 License
This project is licensed under the **MIT License**.

---

## 👨‍💻 Author
**Logic Ninjaz**  
GitHub: https://github.com/Riteshkalkar
