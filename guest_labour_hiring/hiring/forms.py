from django import forms
from django.contrib.auth.models import User
from .models import Worker, Contractor, Job, Feedback, Insurance, NOC, UserProfile


class LoginForm(forms.Form):
    username  = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Username'}))
    password  = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Password'}))
    user_type = forms.ChoiceField(
        choices=[('', 'Select Role'), ('Admin', 'Admin'), ('Police', 'Police'), ('Employer', 'Employer'), ('Worker', 'Worker')],
        widget=forms.Select(attrs={'class': 'form-control'})
    )

class WorkerForm(forms.Form):
    username        = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password        = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    name            = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address         = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    gender          = forms.ChoiceField(choices=[('Male','Male'),('Female','Female'),('Other','Other')], widget=forms.Select(attrs={'class': 'form-control'}))
    phone           = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email           = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    aadhaar_number  = forms.CharField(max_length=12, widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_of_birth   = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    languages_known = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control'}))

class EditWorkerForm(forms.Form):
    username        = forms.CharField(max_length=150,  widget=forms.TextInput(attrs={'class': 'form-control'}))
    new_password    = forms.CharField(required=False,  widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to keep current password'}))
    name            = forms.CharField(max_length=100,  widget=forms.TextInput(attrs={'class': 'form-control'}))
    address         = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    gender          = forms.ChoiceField(choices=[('Male','Male'),('Female','Female'),('Other','Other')], widget=forms.Select(attrs={'class': 'form-control'}))
    phone           = forms.CharField(max_length=15,   widget=forms.TextInput(attrs={'class': 'form-control'}))
    email           = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    aadhaar_number  = forms.CharField(max_length=12,   widget=forms.TextInput(attrs={'class': 'form-control'}))
    date_of_birth   = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    languages_known = forms.CharField(max_length=200,  widget=forms.TextInput(attrs={'class': 'form-control'}))

class ContractorForm(forms.Form):
    username = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    name     = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address  = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    gender   = forms.ChoiceField(choices=[('Male','Male'),('Female','Female'),('Other','Other')], widget=forms.Select(attrs={'class': 'form-control'}))
    phone    = forms.CharField(max_length=15, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email    = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

class EditContractorForm(forms.Form):
    username     = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    new_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to keep current password'}))
    name         = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    address      = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}))
    gender       = forms.ChoiceField(choices=[('Male','Male'),('Female','Female'),('Other','Other')], widget=forms.Select(attrs={'class': 'form-control'}))
    phone        = forms.CharField(max_length=15,  widget=forms.TextInput(attrs={'class': 'form-control'}))
    email        = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))

class PoliceForm(forms.Form):
    username     = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password     = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    name         = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone        = forms.CharField(max_length=15,  widget=forms.TextInput(attrs={'class': 'form-control'}))
    email        = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    badge_number = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

class EditPoliceForm(forms.Form):
    username     = forms.CharField(max_length=150, widget=forms.TextInput(attrs={'class': 'form-control'}))
    new_password = forms.CharField(required=False, widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Leave blank to keep current password'}))
    name         = forms.CharField(max_length=100, widget=forms.TextInput(attrs={'class': 'form-control'}))
    phone        = forms.CharField(max_length=15,  widget=forms.TextInput(attrs={'class': 'form-control'}))
    email        = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control'}))
    badge_number = forms.CharField(max_length=50, required=False, widget=forms.TextInput(attrs={'class': 'form-control'}))

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

class FeedbackForm(forms.ModelForm):
    class Meta:
        model = Feedback
        fields = ['name', 'message']
        widgets = {
            'name':    forms.TextInput(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
        }

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

class NOCRemarkForm(forms.ModelForm):
    class Meta:
        model = NOC
        fields = ['remarks']
        widgets = {
            'remarks': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }
