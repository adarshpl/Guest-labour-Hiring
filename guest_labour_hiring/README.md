# Guest Labour Hiring System
### IGNOU BCA Final Year Project — Django + SQLite/MySQL

---

## 📁 Project Structure
```
guest_labour_hiring/
├── manage.py
├── setup.py                  ← Run once to create admin account
├── guest_labour_hiring/
│   ├── settings.py
│   └── urls.py
└── hiring/
    ├── models.py             ← All database tables
    ├── views.py              ← All logic for 4 roles
    ├── urls.py               ← All routes
    ├── forms.py              ← All forms
    ├── admin.py
    └── templates/hiring/
        ├── base.html
        ├── home.html
        ├── login.html
        ├── admin/            ← Admin templates
        ├── police/           ← Police templates
        ├── employer/         ← Employer templates
        └── worker/           ← Worker templates
```

---

## ⚙️ Setup Instructions

### 1. Install Python & Django
```bash
pip install django
```

### 2. (Optional) For MySQL support:
```bash
pip install mysqlclient
```
Then edit `settings.py` and uncomment the MySQL section.

### 3. Run database migrations
```bash
cd guest_labour_hiring
python manage.py makemigrations
python manage.py migrate
```

### 4. Create Admin & Police test accounts
```bash
python setup.py
```

### 5. Start the server
```bash
python manage.py runserver
```

### 6. Open browser
```
http://127.0.0.1:8000/
```

---

## 🔑 Default Login Credentials (after running setup.py)

| Role    | Username | Password   |
|---------|----------|------------|
| Admin   | admin    | admin123   |
| Police  | police1  | police123  |

> Employers and Workers are created by Admin from the dashboard.

---

## 👥 Role Workflow

### Admin
1. Login → Admin Dashboard
2. Add Workers (creates login + NOC auto-created as Pending)
3. Add Contractors (Employers)
4. View all jobs, requests, manage insurance, view feedback

### Police
1. Login → Police Dashboard
2. View Workers → click Verify → Approve or Reject NOC
3. View all issued NOCs

### Employer
1. Login → Employer Dashboard
2. Post Job Vacancies
3. View Applications → Accept or Reject workers
4. View worker's NOC before hiring

### Worker
1. Login → Worker Dashboard
2. View Profile, NOC Status
3. Browse & Apply for Jobs
4. View Application Status
5. Submit Feedback

---

## 🗄️ Database Tables
- `UserProfile` — Role-based user accounts
- `Worker` — Migrant worker details
- `Contractor` — Employer/contractor details
- `Job` — Job vacancies
- `Request` — Job applications (Pending/Approved/Rejected)
- `NOC` — Police No Objection Certificates
- `Insurance` — Worker insurance records
- `Feedback` — User feedback

---

## 🔒 Security Features
- Django session-based authentication
- `@login_required` decorator on all protected views
- Role-based access control (redirect if wrong role)
- CSRF protection on all forms
- Django ORM (prevents SQL injection)
- Only Admin can create accounts

---

*Built with Python 3 · Django · Bootstrap 5 · SQLite/MySQL*
