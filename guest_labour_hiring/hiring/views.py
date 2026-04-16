from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db import connection
from django.contrib.auth.hashers import make_password
from .forms import (LoginForm, WorkerForm, EditWorkerForm,
                    ContractorForm, EditContractorForm,
                    PoliceForm, EditPoliceForm,
                    JobForm, FeedbackForm, InsuranceForm, NOCRemarkForm)


# ─── Raw SQL helpers ──────────────────────────────────────────────────────────

def sql_fetchall(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        columns = [col[0] for col in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]

def sql_fetchone(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        row = cursor.fetchone()
        if row:
            columns = [col[0] for col in cursor.description]
            return dict(zip(columns, row))
        return None

def sql_execute(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        return cursor.lastrowid

def sql_count(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params or [])
        return cursor.fetchone()[0]


# ─── Helper ───────────────────────────────────────────────────────────────────

def get_role(user):
    try:
        return user.profile.user_type
    except Exception:
        return None


# ─── Public ───────────────────────────────────────────────────────────────────

def home(request):
    return render(request, 'hiring/home.html')

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
                profile = sql_fetchone(
                    "SELECT user_type, status FROM hiring_userprofile WHERE user_id = %s",
                    [user.id]
                )
                if profile and profile['user_type'] == user_type:
                    if profile['status'] == 'Inactive':
                        messages.error(request, 'Your account is inactive. Contact Admin.')
                    else:
                        login(request, user)
                        return redirect('dashboard')
                else:
                    messages.error(request, 'Invalid role selected for this account.')
            else:
                messages.error(request, 'Invalid username or password.')
    return render(request, 'hiring/login.html', {'form': form})

@login_required
def user_logout(request):
    logout(request)
    return redirect('home')

@login_required
def dashboard(request):
    role = get_role(request.user)
    if role == 'Admin':    return redirect('admin_dashboard')
    elif role == 'Police':  return redirect('police_dashboard')
    elif role == 'Employer':return redirect('employer_dashboard')
    elif role == 'Worker':  return redirect('worker_dashboard')
    else:
        logout(request)
        return redirect('login')


# ══════════════════════════════════════════════════════════════════════════════
#  ADMIN
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def admin_dashboard(request):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    stats = {
        'workers':     sql_count("SELECT COUNT(*) FROM hiring_worker"),
        'police':      sql_count("SELECT COUNT(*) FROM hiring_policeofficer"),
        'contractors': sql_count("SELECT COUNT(*) FROM hiring_contractor"),
        'jobs':        sql_count("SELECT COUNT(*) FROM hiring_job"),
        'requests':    sql_count("SELECT COUNT(*) FROM hiring_request"),
        'feedback':    sql_count("SELECT COUNT(*) FROM hiring_feedback"),
    }
    return render(request, 'hiring/admin/dashboard.html', stats)


# ── Workers ──────────────────────────────────────────────────────────────────

@login_required
def admin_add_worker(request):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    form = WorkerForm()
    if request.method == 'POST':
        form = WorkerForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            name = form.cleaned_data['name']
            address = form.cleaned_data['address']
            gender = form.cleaned_data['gender']
            phone = form.cleaned_data['phone']
            email = form.cleaned_data['email']
            aadhaar_number = form.cleaned_data['aadhaar_number']
            date_of_birth = form.cleaned_data['date_of_birth']
            languages_known = form.cleaned_data['languages_known']
            if sql_count("SELECT COUNT(*) FROM auth_user WHERE username = %s", [username]):
                messages.error(request, f'Username "{username}" already exists.')
                return render(request, 'hiring/admin/add_worker.html', {'form': form})
            if sql_count("SELECT COUNT(*) FROM hiring_worker WHERE email = %s", [email]):
                messages.error(request, 'Email already exists.')
                return render(request, 'hiring/admin/add_worker.html', {'form': form})
            if sql_count("SELECT COUNT(*) FROM hiring_worker WHERE aadhaar_number = %s", [aadhaar_number]):
                messages.error(request, 'Aadhaar already exists.')
                return render(request, 'hiring/admin/add_worker.html', {'form': form})
            hashed_pw = make_password(password)
            user_id = sql_execute(
                "INSERT INTO auth_user (username,password,is_active,is_staff,is_superuser,first_name,last_name,email,date_joined) VALUES (%s,%s,1,0,0,'','','',NOW())",
                [username, hashed_pw]
            )
            profile_id = sql_execute(
                "INSERT INTO hiring_userprofile (user_id,user_type,status) VALUES (%s,'Worker','Active')",
                [user_id]
            )
            worker_id = sql_execute(
                "INSERT INTO hiring_worker (name,address,gender,phone,email,aadhaar_number,date_of_birth,languages_known,login_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s)",
                [name, address, gender, phone, email, aadhaar_number, date_of_birth, languages_known, profile_id]
            )
            sql_execute("INSERT INTO hiring_noc (worker_id,status,remarks) VALUES (%s,'Pending','')", [worker_id])
            messages.success(request, f'Worker "{name}" added successfully.')
            return redirect('admin_view_workers')
    return render(request, 'hiring/admin/add_worker.html', {'form': form})


@login_required
def admin_edit_worker(request, wid):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    row = sql_fetchone(
        """SELECT w.wid, w.name, w.address, w.gender, w.phone, w.email,
               w.aadhaar_number, w.date_of_birth, w.languages_known,
               u.username, u.id AS user_id
           FROM hiring_worker w
           JOIN hiring_userprofile p ON w.login_id = p.id
           JOIN auth_user u ON p.user_id = u.id
           WHERE w.wid = %s""",
        [wid]
    )
    if not row:
        messages.error(request, 'Worker not found.')
        return redirect('admin_view_workers')
    if request.method == 'POST':
        form = EditWorkerForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            new_username = d['username']
            new_password = d.get('new_password', '').strip()
            if sql_fetchone("SELECT id FROM auth_user WHERE username=%s AND id!=%s", [new_username, row['user_id']]):
                messages.error(request, f'Username "{new_username}" is already taken.')
                return render(request, 'hiring/admin/edit_worker.html', {'form': form, 'wid': wid, 'worker_name': row['name']})
            if sql_fetchone("SELECT wid FROM hiring_worker WHERE email=%s AND wid!=%s", [d['email'], wid]):
                messages.error(request, 'Email already used by another worker.')
                return render(request, 'hiring/admin/edit_worker.html', {'form': form, 'wid': wid, 'worker_name': row['name']})
            if sql_fetchone("SELECT wid FROM hiring_worker WHERE aadhaar_number=%s AND wid!=%s", [d['aadhaar_number'], wid]):
                messages.error(request, 'Aadhaar already used by another worker.')
                return render(request, 'hiring/admin/edit_worker.html', {'form': form, 'wid': wid, 'worker_name': row['name']})
            sql_execute("UPDATE auth_user SET username=%s WHERE id=%s", [new_username, row['user_id']])
            if new_password:
                sql_execute("UPDATE auth_user SET password=%s WHERE id=%s", [make_password(new_password), row['user_id']])
            sql_execute(
                "UPDATE hiring_worker SET name=%s,address=%s,gender=%s,phone=%s,email=%s,aadhaar_number=%s,date_of_birth=%s,languages_known=%s WHERE wid=%s",
                [d['name'],d['address'],d['gender'],d['phone'],d['email'],d['aadhaar_number'],d['date_of_birth'],d['languages_known'],wid]
            )
            messages.success(request, f'Worker "{d["name"]}" updated successfully.')
            return redirect('admin_view_workers')
    else:
        form = EditWorkerForm(initial={
            'username': row['username'],
            'name': row['name'], 'address': row['address'], 'gender': row['gender'],
            'phone': row['phone'], 'email': row['email'], 'aadhaar_number': row['aadhaar_number'],
            'date_of_birth': row['date_of_birth'], 'languages_known': row['languages_known']
        })
    return render(request, 'hiring/admin/edit_worker.html', {'form': form, 'wid': wid, 'worker_name': row['name']})


@login_required
def admin_view_workers(request):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    rows = sql_fetchall(
        "SELECT w.wid,w.name,w.phone,w.email,w.aadhaar_number,p.status FROM hiring_worker w JOIN hiring_userprofile p ON w.login_id=p.id ORDER BY w.wid"
    )
    class O: pass
    workers = []
    for r in rows:
        obj=O(); obj.wid=r['wid']; obj.name=r['name']; obj.phone=r['phone']
        obj.email=r['email']; obj.aadhaar_number=r['aadhaar_number']
        l=O(); l.status=r['status']; obj.login=l
        workers.append(obj)
    return render(request, 'hiring/admin/view_workers.html', {'workers': workers})


@login_required
def admin_toggle_worker(request, wid):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    row = sql_fetchone("SELECT p.id,p.status FROM hiring_userprofile p JOIN hiring_worker w ON w.login_id=p.id WHERE w.wid=%s", [wid])
    if row:
        new_status = 'Inactive' if row['status'] == 'Active' else 'Active'
        sql_execute("UPDATE hiring_userprofile SET status=%s WHERE id=%s", [new_status, row['id']])
        messages.success(request, f'Worker set to {new_status}.')
    return redirect('admin_view_workers')


@login_required
def admin_delete_worker(request, wid):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    row = sql_fetchone(
        "SELECT u.id AS uid, p.id AS pid FROM auth_user u JOIN hiring_userprofile p ON p.user_id=u.id JOIN hiring_worker w ON w.login_id=p.id WHERE w.wid=%s",
        [wid]
    )
    if row:
        # Delete in order: noc → request → insurance → worker → userprofile → auth_user
        sql_execute("DELETE FROM hiring_noc WHERE worker_id=%s", [wid])
        sql_execute("DELETE FROM hiring_request WHERE worker_id=%s", [wid])
        sql_execute("DELETE FROM hiring_insurance WHERE worker_id=%s", [wid])
        sql_execute("DELETE FROM hiring_worker WHERE wid=%s", [wid])
        sql_execute("DELETE FROM hiring_userprofile WHERE id=%s", [row['pid']])
        sql_execute("DELETE FROM auth_user WHERE id=%s", [row['uid']])
        messages.success(request, 'Worker deleted.')
    return redirect('admin_view_workers')


# ── Police ────────────────────────────────────────────────────────────────────

@login_required
def admin_add_police(request):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    form = PoliceForm()
    if request.method == 'POST':
        form = PoliceForm(request.POST)
        if form.is_valid():
            username     = form.cleaned_data['username']
            password     = form.cleaned_data['password']
            name         = form.cleaned_data['name']
            phone        = form.cleaned_data['phone']
            email        = form.cleaned_data['email']
            badge_number = form.cleaned_data.get('badge_number', '')
            if sql_count("SELECT COUNT(*) FROM auth_user WHERE username=%s", [username]):
                messages.error(request, f'Username "{username}" already exists.')
                return render(request, 'hiring/admin/add_police.html', {'form': form})
            if sql_count("SELECT COUNT(*) FROM hiring_policeofficer WHERE email=%s", [email]):
                messages.error(request, 'Email already exists.')
                return render(request, 'hiring/admin/add_police.html', {'form': form})
            hashed_pw = make_password(password)
            user_id = sql_execute(
                "INSERT INTO auth_user (username,password,is_active,is_staff,is_superuser,first_name,last_name,email,date_joined) VALUES (%s,%s,1,0,0,'','','',NOW())",
                [username, hashed_pw]
            )
            profile_id = sql_execute(
                "INSERT INTO hiring_userprofile (user_id,user_type,status) VALUES (%s,'Police','Active')",
                [user_id]
            )
            sql_execute(
                "INSERT INTO hiring_policeofficer (name,phone,email,badge_number,login_id) VALUES (%s,%s,%s,%s,%s)",
                [name, phone, email, badge_number, profile_id]
            )
            messages.success(request, f'Police officer "{name}" added.')
            return redirect('admin_view_police')
    return render(request, 'hiring/admin/add_police.html', {'form': form})


@login_required
def admin_view_police(request):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    rows = sql_fetchall(
        "SELECT po.pid,po.name,po.phone,po.email,po.badge_number,p.status FROM hiring_policeofficer po JOIN hiring_userprofile p ON po.login_id=p.id ORDER BY po.pid"
    )
    class O: pass
    police_list = []
    for r in rows:
        obj=O(); obj.pid=r['pid']; obj.name=r['name']; obj.phone=r['phone']
        obj.email=r['email']; obj.badge_number=r['badge_number']
        l=O(); l.status=r['status']; obj.login=l
        police_list.append(obj)
    return render(request, 'hiring/admin/view_police.html', {'police_list': police_list})


@login_required
def admin_edit_police(request, pid):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    row = sql_fetchone(
        """SELECT po.pid, po.name, po.phone, po.email, po.badge_number,
               u.username, u.id AS user_id
           FROM hiring_policeofficer po
           JOIN hiring_userprofile p ON po.login_id = p.id
           JOIN auth_user u ON p.user_id = u.id
           WHERE po.pid = %s""",
        [pid]
    )
    if not row:
        messages.error(request, 'Officer not found.')
        return redirect('admin_view_police')
    if request.method == 'POST':
        form = EditPoliceForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            new_username = d['username']
            new_password = d.get('new_password', '').strip()
            if sql_fetchone("SELECT id FROM auth_user WHERE username=%s AND id!=%s", [new_username, row['user_id']]):
                messages.error(request, f'Username "{new_username}" is already taken.')
                return render(request, 'hiring/admin/edit_police.html', {'form': form, 'pid': pid, 'officer_name': row['name']})
            if sql_fetchone("SELECT pid FROM hiring_policeofficer WHERE email=%s AND pid!=%s", [d['email'], pid]):
                messages.error(request, 'Email already used.')
                return render(request, 'hiring/admin/edit_police.html', {'form': form, 'pid': pid, 'officer_name': row['name']})
            sql_execute("UPDATE auth_user SET username=%s WHERE id=%s", [new_username, row['user_id']])
            if new_password:
                sql_execute("UPDATE auth_user SET password=%s WHERE id=%s", [make_password(new_password), row['user_id']])
            sql_execute(
                "UPDATE hiring_policeofficer SET name=%s,phone=%s,email=%s,badge_number=%s WHERE pid=%s",
                [d['name'],d['phone'],d['email'],d.get('badge_number',''),pid]
            )
            messages.success(request, f'Officer "{d["name"]}" updated successfully.')
            return redirect('admin_view_police')
    else:
        form = EditPoliceForm(initial={
            'username': row['username'],
            'name': row['name'], 'phone': row['phone'],
            'email': row['email'], 'badge_number': row['badge_number']
        })
    return render(request, 'hiring/admin/edit_police.html', {'form': form, 'pid': pid, 'officer_name': row['name']})


@login_required
def admin_delete_police(request, pid):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    row = sql_fetchone(
        "SELECT u.id AS uid, p.id AS profile_id FROM auth_user u JOIN hiring_userprofile p ON p.user_id=u.id JOIN hiring_policeofficer po ON po.login_id=p.id WHERE po.pid=%s",
        [pid]
    )
    if row:
        # Update NOCs verified by this officer to NULL first
        sql_execute("UPDATE hiring_noc SET verified_by_id=NULL WHERE verified_by_id=%s", [row['profile_id']])
        sql_execute("DELETE FROM hiring_policeofficer WHERE pid=%s", [pid])
        sql_execute("DELETE FROM hiring_userprofile WHERE id=%s", [row['profile_id']])
        sql_execute("DELETE FROM auth_user WHERE id=%s", [row['uid']])
        messages.success(request, 'Police officer deleted.')
    return redirect('admin_view_police')


# ── Contractors ───────────────────────────────────────────────────────────────

@login_required
def admin_add_contractor(request):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    form = ContractorForm()
    if request.method == 'POST':
        form = ContractorForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            name     = form.cleaned_data['name']
            address  = form.cleaned_data['address']
            gender   = form.cleaned_data['gender']
            phone    = form.cleaned_data['phone']
            email    = form.cleaned_data['email']
            if sql_count("SELECT COUNT(*) FROM auth_user WHERE username=%s", [username]):
                messages.error(request, f'Username "{username}" already exists.')
                return render(request, 'hiring/admin/add_contractor.html', {'form': form})
            if sql_count("SELECT COUNT(*) FROM hiring_contractor WHERE email=%s", [email]):
                messages.error(request, 'Email already exists.')
                return render(request, 'hiring/admin/add_contractor.html', {'form': form})
            hashed_pw = make_password(password)
            user_id = sql_execute(
                "INSERT INTO auth_user (username,password,is_active,is_staff,is_superuser,first_name,last_name,email,date_joined) VALUES (%s,%s,1,0,0,'','','',NOW())",
                [username, hashed_pw]
            )
            profile_id = sql_execute(
                "INSERT INTO hiring_userprofile (user_id,user_type,status) VALUES (%s,'Employer','Active')",
                [user_id]
            )
            sql_execute(
                "INSERT INTO hiring_contractor (name,address,gender,phone,email,login_id) VALUES (%s,%s,%s,%s,%s,%s)",
                [name, address, gender, phone, email, profile_id]
            )
            messages.success(request, 'Contractor added.')
            return redirect('admin_view_contractors')
    return render(request, 'hiring/admin/add_contractor.html', {'form': form})


@login_required
def admin_edit_contractor(request, rid):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    row = sql_fetchone(
        """SELECT c.rid, c.name, c.address, c.gender, c.phone, c.email,
               u.username, u.id AS user_id
           FROM hiring_contractor c
           JOIN hiring_userprofile p ON c.login_id = p.id
           JOIN auth_user u ON p.user_id = u.id
           WHERE c.rid = %s""",
        [rid]
    )
    if not row:
        messages.error(request, 'Contractor not found.')
        return redirect('admin_view_contractors')
    if request.method == 'POST':
        form = EditContractorForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            new_username = d['username']
            new_password = d.get('new_password', '').strip()
            if sql_fetchone("SELECT id FROM auth_user WHERE username=%s AND id!=%s", [new_username, row['user_id']]):
                messages.error(request, f'Username "{new_username}" is already taken.')
                return render(request, 'hiring/admin/edit_contractor.html', {'form': form, 'rid': rid, 'contractor_name': row['name']})
            if sql_fetchone("SELECT rid FROM hiring_contractor WHERE email=%s AND rid!=%s", [d['email'], rid]):
                messages.error(request, 'Email already used.')
                return render(request, 'hiring/admin/edit_contractor.html', {'form': form, 'rid': rid, 'contractor_name': row['name']})
            sql_execute("UPDATE auth_user SET username=%s WHERE id=%s", [new_username, row['user_id']])
            if new_password:
                sql_execute("UPDATE auth_user SET password=%s WHERE id=%s", [make_password(new_password), row['user_id']])
            sql_execute(
                "UPDATE hiring_contractor SET name=%s,address=%s,gender=%s,phone=%s,email=%s WHERE rid=%s",
                [d['name'],d['address'],d['gender'],d['phone'],d['email'],rid]
            )
            messages.success(request, f'Contractor "{d["name"]}" updated successfully.')
            return redirect('admin_view_contractors')
    else:
        form = EditContractorForm(initial={
            'username': row['username'],
            'name': row['name'], 'address': row['address'], 'gender': row['gender'],
            'phone': row['phone'], 'email': row['email']
        })
    return render(request, 'hiring/admin/edit_contractor.html', {'form': form, 'rid': rid, 'contractor_name': row['name']})


@login_required
def admin_view_contractors(request):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    rows = sql_fetchall(
        "SELECT c.rid,c.name,c.phone,c.email,p.status FROM hiring_contractor c JOIN hiring_userprofile p ON c.login_id=p.id ORDER BY c.rid"
    )
    class O: pass
    contractors = []
    for r in rows:
        obj=O(); obj.rid=r['rid']; obj.name=r['name']; obj.phone=r['phone']; obj.email=r['email']
        l=O(); l.status=r['status']; obj.login=l
        contractors.append(obj)
    return render(request, 'hiring/admin/view_contractors.html', {'contractors': contractors})


@login_required
def admin_delete_contractor(request, rid):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    row = sql_fetchone(
        "SELECT u.id AS uid, p.id AS pid FROM auth_user u JOIN hiring_userprofile p ON p.user_id=u.id JOIN hiring_contractor c ON c.login_id=p.id WHERE c.rid=%s",
        [rid]
    )
    if row:
        # Get all job ids for this contractor
        jobs = sql_fetchall("SELECT jid FROM hiring_job WHERE contractor_id=%s", [rid])
        for job in jobs:
            sql_execute("DELETE FROM hiring_request WHERE job_id=%s", [job['jid']])
        sql_execute("DELETE FROM hiring_job WHERE contractor_id=%s", [rid])
        sql_execute("DELETE FROM hiring_contractor WHERE rid=%s", [rid])
        sql_execute("DELETE FROM hiring_userprofile WHERE id=%s", [row['pid']])
        sql_execute("DELETE FROM auth_user WHERE id=%s", [row['uid']])
        messages.success(request, 'Contractor deleted.')
    return redirect('admin_view_contractors')


@login_required
def admin_view_jobs(request):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    rows = sql_fetchall(
        "SELECT j.jid,j.job_name,j.job_type,j.vacancy,j.salary,c.name AS cname FROM hiring_job j JOIN hiring_contractor c ON j.contractor_id=c.rid ORDER BY j.jid"
    )
    class O: pass
    jobs = []
    for r in rows:
        obj=O(); obj.jid=r['jid']; obj.job_name=r['job_name']; obj.job_type=r['job_type']
        obj.vacancy=r['vacancy']; obj.salary=r['salary']
        c=O(); c.name=r['cname']; obj.contractor=c
        jobs.append(obj)
    return render(request, 'hiring/admin/view_jobs.html', {'jobs': jobs})


@login_required
def admin_view_requests(request):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    rows = sql_fetchall(
        "SELECT r.rqid,r.status,w.name AS wname,j.job_name,c.name AS cname FROM hiring_request r JOIN hiring_worker w ON r.worker_id=w.wid JOIN hiring_job j ON r.job_id=j.jid JOIN hiring_contractor c ON j.contractor_id=c.rid ORDER BY r.rqid"
    )
    class O: pass
    reqs = []
    for r in rows:
        obj=O(); obj.rqid=r['rqid']; obj.status=r['status']
        w=O(); w.name=r['wname']; obj.worker=w
        j=O(); j.job_name=r['job_name']; c=O(); c.name=r['cname']; j.contractor=c; obj.job=j
        reqs.append(obj)
    return render(request, 'hiring/admin/view_requests.html', {'requests': reqs})


@login_required
def admin_manage_insurance(request):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    form = InsuranceForm()
    if request.method == 'POST':
        form = InsuranceForm(request.POST)
        if form.is_valid():
            sql_execute(
                "INSERT INTO hiring_insurance (worker_id,insurance_type,insurance_name,amount) VALUES (%s,%s,%s,%s)",
                [form.cleaned_data['worker'].wid, form.cleaned_data['insurance_type'],
                 form.cleaned_data['insurance_name'], form.cleaned_data['amount']]
            )
            messages.success(request, 'Insurance record added.')
            return redirect('admin_manage_insurance')
    rows = sql_fetchall(
        "SELECT i.id,i.insurance_type,i.insurance_name,i.amount,w.name AS wname FROM hiring_insurance i JOIN hiring_worker w ON i.worker_id=w.wid ORDER BY i.id"
    )
    class O: pass
    insurances = []
    for r in rows:
        obj=O(); obj.id=r['id']; obj.insurance_type=r['insurance_type']
        obj.insurance_name=r['insurance_name']; obj.amount=r['amount']
        w=O(); w.name=r['wname']; obj.worker=w
        insurances.append(obj)
    return render(request, 'hiring/admin/manage_insurance.html', {'form': form, 'insurances': insurances})


@login_required
def admin_view_feedback(request):
    if get_role(request.user) != 'Admin': return redirect('dashboard')
    rows = sql_fetchall("SELECT id,name,message,created FROM hiring_feedback ORDER BY created DESC")
    class O: pass
    feedbacks = []
    for r in rows:
        obj=O(); obj.id=r['id']; obj.name=r['name']; obj.message=r['message']; obj.created=r['created']
        feedbacks.append(obj)
    return render(request, 'hiring/admin/view_feedback.html', {'feedbacks': feedbacks})


# ══════════════════════════════════════════════════════════════════════════════
#  POLICE
# ══════════════════════════════════════════════════════════════════════════════

@login_required
def police_dashboard(request):
    if get_role(request.user) != 'Police': return redirect('dashboard')
    stats = {
        'total':    sql_count("SELECT COUNT(*) FROM hiring_worker"),
        'pending':  sql_count("SELECT COUNT(*) FROM hiring_noc WHERE status='Pending'"),
        'approved': sql_count("SELECT COUNT(*) FROM hiring_noc WHERE status='Approved'"),
        'rejected': sql_count("SELECT COUNT(*) FROM hiring_noc WHERE status='Rejected'"),
    }
    return render(request, 'hiring/police/dashboard.html', stats)


@login_required
def police_view_workers(request):
    if get_role(request.user) != 'Police': return redirect('dashboard')
    rows = sql_fetchall(
        "SELECT w.wid,w.name,w.phone,w.aadhaar_number,w.date_of_birth,n.nid,n.status AS noc_status FROM hiring_worker w LEFT JOIN hiring_noc n ON n.worker_id=w.wid ORDER BY w.wid"
    )
    class O: pass
    workers = []
    for r in rows:
        obj=O(); obj.wid=r['wid']; obj.name=r['name']; obj.phone=r['phone']
        obj.aadhaar_number=r['aadhaar_number']; obj.date_of_birth=r['date_of_birth']
        if r['nid']:
            n=O(); n.status=r['noc_status']; obj.noc=n
        else:
            obj.noc=None
        workers.append(obj)
    return render(request, 'hiring/police/view_workers.html', {'workers': workers})


@login_required
def police_issue_noc(request, wid):
    if get_role(request.user) != 'Police': return redirect('dashboard')
    worker_row = sql_fetchone(
        "SELECT wid,name,date_of_birth,gender,phone,email,aadhaar_number,languages_known FROM hiring_worker WHERE wid=%s", [wid]
    )
    if not worker_row:
        messages.error(request, 'Worker not found.')
        return redirect('police_view_workers')
    class O: pass
    worker=O()
    for k,v in worker_row.items(): setattr(worker, k, v)
    noc_row = sql_fetchone("SELECT nid,status,remarks FROM hiring_noc WHERE worker_id=%s", [wid])
    if not noc_row:
        noc_id = sql_execute("INSERT INTO hiring_noc (worker_id,status,remarks) VALUES (%s,'Pending','')", [wid])
        noc_row = {'nid': noc_id, 'status': 'Pending', 'remarks': ''}
    noc=O(); noc.nid=noc_row['nid']; noc.status=noc_row['status']; noc.remarks=noc_row['remarks']
    from .models import NOC as NOCModel
    noc_model_instance = NOCModel.objects.get(nid=noc_row['nid'])
    form = NOCRemarkForm(instance=noc_model_instance)
    if request.method == 'POST':
        action  = request.POST.get('action')
        remarks = request.POST.get('remarks', '')
        status  = 'Approved' if action == 'approve' else 'Rejected'
        profile_row = sql_fetchone("SELECT id FROM hiring_userprofile WHERE user_id=%s", [request.user.id])
        sql_execute(
            "UPDATE hiring_noc SET status=%s,remarks=%s,verified_by_id=%s WHERE nid=%s",
            [status, remarks, profile_row['id'], noc_row['nid']]
        )
        messages.success(request, f'NOC {status} for {worker.name}.')
        return redirect('police_view_workers')
    return render(request, 'hiring/police/issue_noc.html', {'worker': worker, 'noc': noc, 'form': form})


@login_required
def police_view_nocs(request):
    if get_role(request.user) != 'Police': return redirect('dashboard')
    rows = sql_fetchall(
        "SELECT n.nid,n.status,n.remarks,w.name AS wname,u.username AS vby FROM hiring_noc n JOIN hiring_worker w ON n.worker_id=w.wid LEFT JOIN hiring_userprofile p ON n.verified_by_id=p.id LEFT JOIN auth_user u ON p.user_id=u.id ORDER BY n.nid"
    )
    class O: pass
    nocs = []
    for r in rows:
        obj=O(); obj.nid=r['nid']; obj.status=r['status']; obj.remarks=r['remarks']
        w=O(); w.name=r['wname']; obj.worker=w
        vb=O(); vu=O(); vu.username=r['vby'] or 'Pending'; vb.user=vu; obj.verified_by=vb
        nocs.append(obj)
    return render(request, 'hiring/police/view_nocs.html', {'nocs': nocs})


# ══════════════════════════════════════════════════════════════════════════════
#  EMPLOYER
# ══════════════════════════════════════════════════════════════════════════════

def _get_contractor_rid(user):
    p = sql_fetchone("SELECT id FROM hiring_userprofile WHERE user_id=%s", [user.id])
    c = sql_fetchone("SELECT rid FROM hiring_contractor WHERE login_id=%s", [p['id']])
    return c['rid']

@login_required
def employer_dashboard(request):
    if get_role(request.user) != 'Employer': return redirect('dashboard')
    rid = _get_contractor_rid(request.user)
    stats = {
        'jobs':     sql_count("SELECT COUNT(*) FROM hiring_job WHERE contractor_id=%s", [rid]),
        'pending':  sql_count("SELECT COUNT(*) FROM hiring_request r JOIN hiring_job j ON r.job_id=j.jid WHERE j.contractor_id=%s AND r.status='Pending'", [rid]),
        'approved': sql_count("SELECT COUNT(*) FROM hiring_request r JOIN hiring_job j ON r.job_id=j.jid WHERE j.contractor_id=%s AND r.status='Approved'", [rid]),
    }
    return render(request, 'hiring/employer/dashboard.html', stats)

@login_required
def employer_add_job(request):
    if get_role(request.user) != 'Employer': return redirect('dashboard')
    rid = _get_contractor_rid(request.user)
    form = JobForm()
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            d = form.cleaned_data
            sql_execute(
                "INSERT INTO hiring_job (job_name,job_type,description,vacancy,qualification,experience,salary,contractor_id) VALUES (%s,%s,%s,%s,%s,%s,%s,%s)",
                [d['job_name'],d['job_type'],d['description'],d['vacancy'],d['qualification'],d['experience'],d['salary'],rid]
            )
            messages.success(request, 'Job vacancy posted.')
            return redirect('employer_view_jobs')
    return render(request, 'hiring/employer/add_job.html', {'form': form})

@login_required
def employer_view_jobs(request):
    if get_role(request.user) != 'Employer': return redirect('dashboard')
    rid = _get_contractor_rid(request.user)
    rows = sql_fetchall("SELECT jid,job_name,job_type,vacancy,experience,salary,qualification FROM hiring_job WHERE contractor_id=%s ORDER BY jid", [rid])
    class O: pass
    jobs=[]
    for r in rows:
        obj=O()
        for k,v in r.items(): setattr(obj,k,v)
        jobs.append(obj)
    return render(request, 'hiring/employer/view_jobs.html', {'jobs': jobs})

@login_required
def employer_view_applications(request):
    if get_role(request.user) != 'Employer': return redirect('dashboard')
    rid = _get_contractor_rid(request.user)
    rows = sql_fetchall(
        "SELECT r.rqid,r.status,w.wid,w.name AS wname,j.job_name FROM hiring_request r JOIN hiring_worker w ON r.worker_id=w.wid JOIN hiring_job j ON r.job_id=j.jid WHERE j.contractor_id=%s ORDER BY r.rqid",
        [rid]
    )
    class O: pass
    apps=[]
    for r in rows:
        obj=O(); obj.rqid=r['rqid']; obj.status=r['status']
        w=O(); w.wid=r['wid']; w.name=r['wname']; obj.worker=w
        j=O(); j.job_name=r['job_name']; obj.job=j
        apps.append(obj)
    return render(request, 'hiring/employer/view_applications.html', {'applications': apps})

@login_required
def employer_action_request(request, rqid, action):
    if get_role(request.user) != 'Employer': return redirect('dashboard')
    new_status = 'Approved' if action == 'approve' else 'Rejected'
    sql_execute("UPDATE hiring_request SET status=%s WHERE rqid=%s", [new_status, rqid])
    messages.success(request, f'Application {new_status}.')
    return redirect('employer_view_applications')

@login_required
def employer_view_worker_noc(request, wid):
    if get_role(request.user) != 'Employer': return redirect('dashboard')
    wr = sql_fetchone("SELECT wid,name FROM hiring_worker WHERE wid=%s", [wid])
    nr = sql_fetchone("SELECT status,remarks FROM hiring_noc WHERE worker_id=%s", [wid])
    class O: pass
    worker=O(); worker.wid=wr['wid']; worker.name=wr['name']
    noc=None
    if nr:
        noc=O(); noc.status=nr['status']; noc.remarks=nr['remarks']
    return render(request, 'hiring/employer/view_worker_noc.html', {'worker': worker, 'noc': noc})


# ══════════════════════════════════════════════════════════════════════════════
#  WORKER
# ══════════════════════════════════════════════════════════════════════════════

def _get_worker_wid(user):
    p = sql_fetchone("SELECT id FROM hiring_userprofile WHERE user_id=%s", [user.id])
    w = sql_fetchone("SELECT wid FROM hiring_worker WHERE login_id=%s", [p['id']])
    return w['wid']

@login_required
def worker_dashboard(request):
    if get_role(request.user) != 'Worker': return redirect('dashboard')
    wid = _get_worker_wid(request.user)
    nr = sql_fetchone("SELECT status FROM hiring_noc WHERE worker_id=%s", [wid])
    class O: pass
    wr=O(); wr.wid=wid
    p=sql_fetchone("SELECT id FROM hiring_userprofile WHERE user_id=%s",[request.user.id])
    wr_row=sql_fetchone("SELECT name FROM hiring_worker WHERE login_id=%s",[p['id']])
    wr.name=wr_row['name']
    stats={
        'worker': wr,
        'applications': sql_count("SELECT COUNT(*) FROM hiring_request WHERE worker_id=%s",[wid]),
        'approved':     sql_count("SELECT COUNT(*) FROM hiring_request WHERE worker_id=%s AND status='Approved'",[wid]),
        'noc_status':   nr['status'] if nr else 'Pending',
    }
    return render(request, 'hiring/worker/dashboard.html', stats)

@login_required
def worker_profile(request):
    if get_role(request.user) != 'Worker': return redirect('dashboard')
    p=sql_fetchone("SELECT id FROM hiring_userprofile WHERE user_id=%s",[request.user.id])
    row=sql_fetchone("SELECT wid,name,address,gender,phone,email,aadhaar_number,date_of_birth,languages_known FROM hiring_worker WHERE login_id=%s",[p['id']])
    class O: pass
    worker=O()
    for k,v in row.items(): setattr(worker,k,v)
    return render(request, 'hiring/worker/profile.html', {'worker': worker})

@login_required
def worker_noc_status(request):
    if get_role(request.user) != 'Worker': return redirect('dashboard')
    wid=_get_worker_wid(request.user)
    nr=sql_fetchone("SELECT status,remarks FROM hiring_noc WHERE worker_id=%s",[wid])
    class O: pass
    noc=None
    if nr:
        noc=O(); noc.status=nr['status']; noc.remarks=nr['remarks']
    return render(request, 'hiring/worker/noc_status.html', {'noc': noc})

@login_required
def worker_view_jobs(request):
    if get_role(request.user) != 'Worker': return redirect('dashboard')
    wid=_get_worker_wid(request.user)
    rows=sql_fetchall(
        "SELECT j.jid,j.job_name,j.job_type,j.vacancy,j.experience,j.salary,j.qualification,j.description,c.name AS cname FROM hiring_job j JOIN hiring_contractor c ON j.contractor_id=c.rid WHERE j.jid NOT IN (SELECT job_id FROM hiring_request WHERE worker_id=%s) ORDER BY j.jid",
        [wid]
    )
    class O: pass
    jobs=[]
    for r in rows:
        obj=O()
        for k,v in r.items(): setattr(obj,k,v)
        c=O(); c.name=r['cname']; obj.contractor=c
        jobs.append(obj)
    return render(request, 'hiring/worker/view_jobs.html', {'jobs': jobs})

@login_required
def worker_apply_job(request, jid):
    if get_role(request.user) != 'Worker': return redirect('dashboard')
    wid=_get_worker_wid(request.user)
    jr=sql_fetchone("SELECT jid,job_name FROM hiring_job WHERE jid=%s",[jid])
    if not jr:
        messages.error(request, 'Job not found.')
        return redirect('worker_view_jobs')
    if not sql_count("SELECT COUNT(*) FROM hiring_request WHERE worker_id=%s AND job_id=%s",[wid,jid]):
        sql_execute("INSERT INTO hiring_request (worker_id,job_id,status) VALUES (%s,%s,'Pending')",[wid,jid])
        messages.success(request, f'Applied for "{jr["job_name"]}" successfully.')
    else:
        messages.warning(request, 'Already applied for this job.')
    return redirect('worker_view_jobs')

@login_required
def worker_application_status(request):
    if get_role(request.user) != 'Worker': return redirect('dashboard')
    wid=_get_worker_wid(request.user)
    rows=sql_fetchall(
        "SELECT r.rqid,r.status,j.job_name,j.salary,c.name AS cname FROM hiring_request r JOIN hiring_job j ON r.job_id=j.jid JOIN hiring_contractor c ON j.contractor_id=c.rid WHERE r.worker_id=%s ORDER BY r.rqid",
        [wid]
    )
    class O: pass
    apps=[]
    for r in rows:
        obj=O(); obj.rqid=r['rqid']; obj.status=r['status']
        j=O(); j.job_name=r['job_name']; j.salary=r['salary']
        c=O(); c.name=r['cname']; j.contractor=c; obj.job=j
        apps.append(obj)
    return render(request, 'hiring/worker/application_status.html', {'applications': apps})

@login_required
def worker_feedback(request):
    if get_role(request.user) != 'Worker': return redirect('dashboard')
    form=FeedbackForm()
    if request.method == 'POST':
        form=FeedbackForm(request.POST)
        if form.is_valid():
            sql_execute("INSERT INTO hiring_feedback (name,message,created) VALUES (%s,%s,NOW())",
                [form.cleaned_data['name'],form.cleaned_data['message']])
            messages.success(request, 'Thank you for your feedback!')
            return redirect('worker_dashboard')
    return render(request, 'hiring/worker/feedback.html', {'form': form})
