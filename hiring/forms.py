from django import forms
from django.contrib.auth.models import User
from .models import Worker, Contractor, Job, Feedback, Insurance, NOC, UserProfile


# ─── Login Form ──────────────────────────────────────────────────────────────
class LoginForm(forms.Form):
    username  = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password  = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    user_type = forms.ChoiceField(
        choices=[('', 'Select Role'), ('Admin', 'Admin'), ('Police', 'Police'), ('Employer', 'Employer'), ('Worker', 'Worker')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )


# ─── Add Worker Form ─────────────────────────────────────────────────────────
class WorkerForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Worker
        fields = ['name', 'address', 'gender', 'phone', 'email', 'aadhaar_number', 'date_of_birth', 'languages_known']
        widgets = {
            'name':            forms.TextInput(attrs={'class': 'form-control'}),
            'address':         forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'gender':          forms.Select(attrs={'class': 'form-control'}),
            'phone':           forms.TextInput(attrs={'class': 'form-control'}),
            'email':           forms.EmailInput(attrs={'class': 'form-control'}),
            'aadhaar_number':  forms.TextInput(attrs={'class': 'form-control', 'maxlength': '12'}),
            'date_of_birth':   forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'languages_known': forms.TextInput(attrs={'class': 'form-control'}),
        }


# ─── Add Contractor Form ─────────────────────────────────────────────────────
class ContractorForm(forms.ModelForm):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Contractor
        fields = ['name', 'address', 'gender', 'phone', 'email']
        widgets = {
            'name':    forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'gender':  forms.Select(attrs={'class': 'form-control'}),
            'phone':   forms.TextInput(attrs={'class': 'form-control'}),
            'email':   forms.EmailInput(attrs={'class': 'form-control'}),
        }


# ─── Job Form ────────────────────────────────────────────────────────────────
class JobForm(forms.ModelForm):
    class Meta:
        model = Job
        fields = ['job_name', 'job_type', 'description', 'vacancy', 'qualification', 'experience', 'salary']
        widgets = {
            'job_name':      forms.TextInput(attrs={'class': 'form-control'}),
            'job_type':      forms.TextInput(attrs={'class': 'form-control'}),
            'description':   forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'vacancy':       forms.NumberInput(attrs={'class': 'form-control'}),
            'qualification': forms.TextInput(attrs={'class': 'form-control'}),
            'experience':    forms.TextInput(attrs={'class': 'form-control'}),
            'salary':        forms.NumberInput(attrs={'class': 'form-control'}),
        }


# ─── Feedback Form ───────────────────────────────────────────────────────────
class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'message']
        widgets = {
            'name':    forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }


# ─── Insurance Form ──────────────────────────────────────────────────────────
class InsuranceForm(forms.ModelForm):
    class Meta:
        model = Insurance
        fields = ['worker', 'insurance_type', 'insurance_name', 'amount']
        widgets = {
            'worker':         forms.Select(attrs={'class': 'form-control'}),
            'insurance_type': forms.TextInput(attrs={'class': 'form-control'}),
            'insurance_name': forms.TextInput(attrs={'class': 'form-control'}),
            'amount':         forms.NumberInput(attrs={'class': 'form-control'}),
        }


# ─── NOC Remark Form ─────────────────────────────────────────────────────────
class NOCRemarkForm(forms.ModelForm):
    class Meta:
        model = NOC
        fields = ['remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
