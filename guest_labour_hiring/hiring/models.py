from django.db import models
from django.contrib.auth.models import User

# ─── User Profile (extends Django's built-in User) ───────────────────────────
class UserProfile(models.Model):
    """Maps each Django user to a role in the system."""
    USER_TYPE_CHOICES = [
        ('Admin',    'Admin'),
        ('Police',   'Police'),
        ('Employer', 'Employer'),
        ('Worker',   'Worker'),
    ]
    STATUS_CHOICES = [
        ('Active',   'Active'),
        ('Inactive', 'Inactive'),
    ]
    user      = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    status    = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')

    def __str__(self):
        return f"{self.user.username} ({self.user_type})"


# ─── Worker ──────────────────────────────────────────────────────────────────
class Worker(models.Model):
    """Stores migrant worker personal details."""
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]

    wid             = models.AutoField(primary_key=True)
    name            = models.CharField(max_length=100)
    address         = models.TextField()
    gender          = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone           = models.CharField(max_length=15)
    email           = models.EmailField(unique=True)
    aadhaar_number  = models.CharField(max_length=12, unique=True)
    date_of_birth   = models.DateField()
    languages_known = models.CharField(max_length=200)
    login           = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='worker_profile')

    def __str__(self):
        return self.name


# ─── Contractor (Employer) ───────────────────────────────────────────────────
class Contractor(models.Model):
    """Stores employer/contractor details."""
    GENDER_CHOICES = [('Male', 'Male'), ('Female', 'Female'), ('Other', 'Other')]

    rid     = models.AutoField(primary_key=True)
    name    = models.CharField(max_length=100)
    address = models.TextField()
    gender  = models.CharField(max_length=10, choices=GENDER_CHOICES)
    phone   = models.CharField(max_length=15)
    email   = models.EmailField(unique=True)
    login   = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='contractor_profile')

    def __str__(self):
        return self.name


# ─── Job ─────────────────────────────────────────────────────────────────────
class Job(models.Model):
    """Job vacancies posted by contractors."""
    jid         = models.AutoField(primary_key=True)
    job_name    = models.CharField(max_length=100)
    job_type    = models.CharField(max_length=100)
    description = models.TextField()
    vacancy     = models.PositiveIntegerField()
    qualification = models.CharField(max_length=200)
    experience  = models.CharField(max_length=100)
    salary      = models.DecimalField(max_digits=10, decimal_places=2)
    contractor  = models.ForeignKey(Contractor, on_delete=models.CASCADE, related_name='jobs')

    def __str__(self):
        return f"{self.job_name} by {self.contractor.name}"


# ─── Request (Job Application) ───────────────────────────────────────────────
class Request(models.Model):
    """Workers apply for jobs; tracked here."""
    STATUS_CHOICES = [
        ('Pending',  'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    rqid   = models.AutoField(primary_key=True)
    job    = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    worker = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')

    class Meta:
        unique_together = ('job', 'worker')  # prevent duplicate applications

    def __str__(self):
        return f"{self.worker.name} → {self.job.job_name} [{self.status}]"


# ─── NOC (No Objection Certificate) ─────────────────────────────────────────
class NOC(models.Model):
    """Police-issued NOC for each worker."""
    STATUS_CHOICES = [
        ('Pending',  'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]
    nid         = models.AutoField(primary_key=True)
    worker      = models.OneToOneField(Worker, on_delete=models.CASCADE, related_name='noc')
    status      = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    remarks     = models.TextField(blank=True)
    verified_by = models.ForeignKey(UserProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='verified_nocs')

    def __str__(self):
        return f"NOC for {self.worker.name} [{self.status}]"


# ─── Insurance ───────────────────────────────────────────────────────────────
class Insurance(models.Model):
    """Insurance records for workers."""
    worker         = models.ForeignKey(Worker, on_delete=models.CASCADE, related_name='insurances')
    insurance_type = models.CharField(max_length=100)
    insurance_name = models.CharField(max_length=100)
    amount         = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.insurance_name} for {self.worker.name}"


# ─── Feedback ────────────────────────────────────────────────────────────────
class Feedback(models.Model):
    """Public/worker feedback submitted via the website."""
    name    = models.CharField(max_length=100)
    message = models.TextField()
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Feedback from {self.name}"


# ─── Police Officer ───────────────────────────────────────────────────────────
class PoliceOfficer(models.Model):
    """Stores police officer personal details."""
    pid          = models.AutoField(primary_key=True)
    name         = models.CharField(max_length=100)
    phone        = models.CharField(max_length=15)
    email        = models.EmailField(unique=True)
    badge_number = models.CharField(max_length=50, blank=True)
    login        = models.OneToOneField(UserProfile, on_delete=models.CASCADE, related_name='police_profile')

    def __str__(self):
        return self.name
