from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import Worker, Contractor, Job, Request, NOC, Insurance, Feedback, UserProfile
from .forms import LoginForm, WorkerForm, ContractorForm, JobForm, FeedbackForm, InsuranceForm, NOCRemarkForm


# ─── Helper: get role ─────────────────────────────────────────────────────────
def get_role(user):
    try:
        return user.profile.user_type
    except Exception:
        return None


# ─── Home Page ────────────────────────────────────────────────────────────────
def home(request):
    return render(request, 'hiring/home.html')


# ─── Login ────────────────────────────────────────────────────────────────────
def user_login(request):
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username  = form.cleaned_data['username']
            password  = form.cleaned_data['password']
            user_type = form.cleaned_data['user_type']
            user = authenticate(request, username=username, password=password)
            if user:
                profile = getattr(user, 'profile', None)
                if profile and profile.user_type == user_type:
                    if profile.status == 'Inactive':
                        messages.error(request, 'Your account is inactive. Contact Admin.')
                    else:
                        login(request, user)
                        return redirect('dashboard')
                else:
                    messages.error(request, 'Invalid role selected for this account.')
            else:
                messages.error(request, 'Invalid username or password.')
    return render(request, 'hiring/login.html', {'form': form})


# ─── Logout ───────────────────────────────────────────────────────────────────
@login_required
def user_logout(request):
    logout(request)
    return redirect('home')


# ─── Dashboard Router ─────────────────────────────────────────────────────────
@login_required
def dashboard(request):
    role = get_role(request.user)
    if role == 'Admin':
        return redirect('admin_dashboard')
    elif role == 'Police':
        return redirect('police_dashboard')
    elif role == 'Employer':
        return redirect('employer_dashboard')
    elif role == 'Worker':
        return redirect('worker_dashboard')
    else:
        logout(request)
        return redirect('login')


# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN VIEWS
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def admin_dashboard(request):
    if get_role(request.user) != 'Admin':
        return redirect('dashboard')
    stats = {
        'workers':     Worker.objects.count(),
        'contractors': Contractor.objects.count(),
        'jobs':        Job.objects.count(),
        'requests':    Request.objects.count(),
        'feedback':    Feedback.objects.count(),
    }
    return render(request, 'hiring/admin/dashboard.html', stats)


@login_required
def admin_add_worker(request):
    if get_role(request.user) != 'Admin':
        return redirect('dashboard')
    form = WorkerForm()
    if request.method == 'POST':
        form = WorkerForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            # Check if username already exists
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Username "{username}" already exists. Please choose a different username.')
                return render(request, 'hiring/admin/add_worker.html', {'form': form})
            # Check if email already exists
            if Worker.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, 'A worker with this email already exists.')
                return render(request, 'hiring/admin/add_worker.html', {'form': form})
            # Check if Aadhaar already exists
            if Worker.objects.filter(aadhaar_number=form.cleaned_data['aadhaar_number']).exists():
                messages.error(request, 'A worker with this Aadhaar number already exists.')
                return render(request, 'hiring/admin/add_worker.html', {'form': form})
            # Create Django user
            u = User.objects.create_user(
                username=username,
                password=form.cleaned_data['password']
            )
            profile = UserProfile.objects.create(user=u, user_type='Worker')
            noc_pending = form.save(commit=False)
            noc_pending.login = profile
            noc_pending.save()
            # Create a pending NOC automatically
            NOC.objects.create(worker=noc_pending, status='Pending')
            messages.success(request, f'Worker "{noc_pending.name}" added successfully.')
            return redirect('admin_view_workers')
    return render(request, 'hiring/admin/add_worker.html', {'form': form})


@login_required
def admin_view_workers(request):
    if get_role(request.user) != 'Admin':
        return redirect('dashboard')
    workers = Worker.objects.select_related('login').all()
    return render(request, 'hiring/admin/view_workers.html', {'workers': workers})


@login_required
def admin_toggle_worker(request, wid):
    """Activate or deactivate a worker account."""
    if get_role(request.user) != 'Admin':
        return redirect('dashboard')
    worker = get_object_or_404(Worker, wid=wid)
    profile = worker.login
    profile.status = 'Inactive' if profile.status == 'Active' else 'Active'
    profile.save()
    messages.success(request, f'Worker account set to {profile.status}.')
    return redirect('admin_view_workers')


@login_required
def admin_delete_worker(request, wid):
    if get_role(request.user) != 'Admin':
        return redirect('dashboard')
    worker = get_object_or_404(Worker, wid=wid)
    worker.login.user.delete()  # cascades to profile → worker
    messages.success(request, 'Worker deleted.')
    return redirect('admin_view_workers')


@login_required
def admin_add_contractor(request):
    if get_role(request.user) != 'Admin':
        return redirect('dashboard')
    form = ContractorForm()
    if request.method == 'POST':
        form = ContractorForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            if User.objects.filter(username=username).exists():
                messages.error(request, f'Username "{username}" already exists. Please choose a different username.')
                return render(request, 'hiring/admin/add_contractor.html', {'form': form})
            if Contractor.objects.filter(email=form.cleaned_data['email']).exists():
                messages.error(request, 'A contractor with this email already exists.')
                return render(request, 'hiring/admin/add_contractor.html', {'form': form})
            u = User.objects.create_user(username=username, password=form.cleaned_data['password'])
            profile = UserProfile.objects.create(user=u, user_type='Employer')
            c = form.save(commit=False)
            c.login = profile
            c.save()
            messages.success(request, f'Contractor added successfully.')
            return redirect('admin_view_contractors')
    return render(request, 'hiring/admin/add_contractor.html', {'form': form})


@login_required
def admin_view_contractors(request):
    if get_role(request.user) != 'Admin':
        return redirect('dashboard')
    contractors = Contractor.objects.select_related('login').all()
    return render(request, 'hiring/admin/view_contractors.html', {'contractors': contractors})


@login_required
def admin_delete_contractor(request, rid):
    if get_role(request.user) != 'Admin':
        return redirect('dashboard')
    contractor = get_object_or_404(Contractor, rid=rid)
    contractor.login.user.delete()
    messages.success(request, 'Contractor deleted.')
    return redirect('admin_view_contractors')


@login_required
def admin_view_jobs(request):
    if get_role(request.user) != 'Admin':
        return redirect('dashboard')
    jobs = Job.objects.select_related('contractor').all()
    return render(request, 'hiring/admin/view_jobs.html', {'jobs': jobs})


@login_required
def admin_view_requests(request):
    if get_role(request.user) != 'Admin':
        return redirect('dashboard')
    reqs = Request.objects.select_related('job', 'worker').all()
    return render(request, 'hiring/admin/view_requests.html', {'requests': reqs})


@login_required
def admin_manage_insurance(request):
    if get_role(request.user) != 'Admin':
        return redirect('dashboard')
    form = InsuranceForm()
    insurances = Insurance.objects.select_related('worker').all()
    if request.method == 'POST':
        form = InsuranceForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Insurance record added.')
            return redirect('admin_manage_insurance')
    return render(request, 'hiring/admin/manage_insurance.html', {'form': form, 'insurances': insurances})


@login_required
def admin_view_feedback(request):
    if get_role(request.user) != 'Admin':
        return redirect('dashboard')
    feedbacks = Feedback.objects.order_by('-created')
    return render(request, 'hiring/admin/view_feedback.html', {'feedbacks': feedbacks})


# ══════════════════════════════════════════════════════════════════════════════
#  POLICE VIEWS
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def police_dashboard(request):
    if get_role(request.user) != 'Police':
        return redirect('dashboard')
    stats = {
        'total':    Worker.objects.count(),
        'pending':  NOC.objects.filter(status='Pending').count(),
        'approved': NOC.objects.filter(status='Approved').count(),
        'rejected': NOC.objects.filter(status='Rejected').count(),
    }
    return render(request, 'hiring/police/dashboard.html', stats)


@login_required
def police_view_workers(request):
    if get_role(request.user) != 'Police':
        return redirect('dashboard')
    workers = Worker.objects.prefetch_related('noc').all()
    return render(request, 'hiring/police/view_workers.html', {'workers': workers})


@login_required
def police_issue_noc(request, wid):
    """Approve or reject a worker's NOC."""
    if get_role(request.user) != 'Police':
        return redirect('dashboard')
    worker = get_object_or_404(Worker, wid=wid)
    noc, _ = NOC.objects.get_or_create(worker=worker)
    form = NOCRemarkForm(instance=noc)
    if request.method == 'POST':
        action = request.POST.get('action')
        form = NOCRemarkForm(request.POST, instance=noc)
        if form.is_valid():
            noc_obj = form.save(commit=False)
            noc_obj.status = 'Approved' if action == 'approve' else 'Rejected'
            noc_obj.verified_by = request.user.profile
            noc_obj.save()
            messages.success(request, f'NOC {noc_obj.status} for {worker.name}.')
            return redirect('police_view_workers')
    return render(request, 'hiring/police/issue_noc.html', {'worker': worker, 'noc': noc, 'form': form})


@login_required
def police_view_nocs(request):
    if get_role(request.user) != 'Police':
        return redirect('dashboard')
    nocs = NOC.objects.select_related('worker', 'verified_by').all()
    return render(request, 'hiring/police/view_nocs.html', {'nocs': nocs})


# ══════════════════════════════════════════════════════════════════════════════
#  EMPLOYER VIEWS
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def employer_dashboard(request):
    if get_role(request.user) != 'Employer':
        return redirect('dashboard')
    contractor = get_object_or_404(Contractor, login=request.user.profile)
    stats = {
        'jobs':     Job.objects.filter(contractor=contractor).count(),
        'pending':  Request.objects.filter(job__contractor=contractor, status='Pending').count(),
        'approved': Request.objects.filter(job__contractor=contractor, status='Approved').count(),
    }
    return render(request, 'hiring/employer/dashboard.html', stats)


@login_required
def employer_add_job(request):
    if get_role(request.user) != 'Employer':
        return redirect('dashboard')
    contractor = get_object_or_404(Contractor, login=request.user.profile)
    form = JobForm()
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.contractor = contractor
            job.save()
            messages.success(request, 'Job vacancy posted.')
            return redirect('employer_view_jobs')
    return render(request, 'hiring/employer/add_job.html', {'form': form})


@login_required
def employer_view_jobs(request):
    if get_role(request.user) != 'Employer':
        return redirect('dashboard')
    contractor = get_object_or_404(Contractor, login=request.user.profile)
    jobs = Job.objects.filter(contractor=contractor)
    return render(request, 'hiring/employer/view_jobs.html', {'jobs': jobs})


@login_required
def employer_view_applications(request):
    if get_role(request.user) != 'Employer':
        return redirect('dashboard')
    contractor = get_object_or_404(Contractor, login=request.user.profile)
    applications = Request.objects.filter(job__contractor=contractor).select_related('job', 'worker')
    return render(request, 'hiring/employer/view_applications.html', {'applications': applications})


@login_required
def employer_action_request(request, rqid, action):
    """Accept or reject a worker application."""
    if get_role(request.user) != 'Employer':
        return redirect('dashboard')
    req = get_object_or_404(Request, rqid=rqid)
    req.status = 'Approved' if action == 'approve' else 'Rejected'
    req.save()
    messages.success(request, f'Application {req.status}.')
    return redirect('employer_view_applications')


@login_required
def employer_view_worker_noc(request, wid):
    if get_role(request.user) != 'Employer':
        return redirect('dashboard')
    worker = get_object_or_404(Worker, wid=wid)
    noc = getattr(worker, 'noc', None)
    return render(request, 'hiring/employer/view_worker_noc.html', {'worker': worker, 'noc': noc})


# ══════════════════════════════════════════════════════════════════════════════
#  WORKER VIEWS
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def worker_dashboard(request):
    if get_role(request.user) != 'Worker':
        return redirect('dashboard')
    worker = get_object_or_404(Worker, login=request.user.profile)
    stats = {
        'applications': Request.objects.filter(worker=worker).count(),
        'approved':     Request.objects.filter(worker=worker, status='Approved').count(),
    }
    return render(request, 'hiring/worker/dashboard.html', {'worker': worker, **stats})


@login_required
def worker_profile(request):
    if get_role(request.user) != 'Worker':
        return redirect('dashboard')
    worker = get_object_or_404(Worker, login=request.user.profile)
    return render(request, 'hiring/worker/profile.html', {'worker': worker})


@login_required
def worker_noc_status(request):
    if get_role(request.user) != 'Worker':
        return redirect('dashboard')
    worker = get_object_or_404(Worker, login=request.user.profile)
    noc = getattr(worker, 'noc', None)
    return render(request, 'hiring/worker/noc_status.html', {'noc': noc})


@login_required
def worker_view_jobs(request):
    if get_role(request.user) != 'Worker':
        return redirect('dashboard')
    worker = get_object_or_404(Worker, login=request.user.profile)
    applied_job_ids = Request.objects.filter(worker=worker).values_list('job_id', flat=True)
    jobs = Job.objects.exclude(jid__in=applied_job_ids)
    return render(request, 'hiring/worker/view_jobs.html', {'jobs': jobs})


@login_required
def worker_apply_job(request, jid):
    if get_role(request.user) != 'Worker':
        return redirect('dashboard')
    worker = get_object_or_404(Worker, login=request.user.profile)
    job = get_object_or_404(Job, jid=jid)
    if not Request.objects.filter(worker=worker, job=job).exists():
        Request.objects.create(worker=worker, job=job, status='Pending')
        messages.success(request, f'Applied for "{job.job_name}" successfully.')
    else:
        messages.warning(request, 'You have already applied for this job.')
    return redirect('worker_view_jobs')


@login_required
def worker_application_status(request):
    if get_role(request.user) != 'Worker':
        return redirect('dashboard')
    worker = get_object_or_404(Worker, login=request.user.profile)
    applications = Request.objects.filter(worker=worker).select_related('job')
    return render(request, 'hiring/worker/application_status.html', {'applications': applications})


@login_required
def worker_feedback(request):
    if get_role(request.user) != 'Worker':
        return redirect('dashboard')
    form = FeedbackForm()
    if request.method == 'POST':
        form = FeedbackForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Thank you for your feedback!')
            return redirect('worker_dashboard')
    return render(request, 'hiring/worker/feedback.html', {'form': form})
