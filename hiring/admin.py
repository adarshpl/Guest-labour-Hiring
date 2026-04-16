from django.contrib import admin
from .models import UserProfile, Worker, Contractor, Job, Request, NOC, Insurance, Feedback

admin.site.register(UserProfile)
admin.site.register(Worker)
admin.site.register(Contractor)
admin.site.register(Job)
admin.site.register(Request)
admin.site.register(NOC)
admin.site.register(Insurance)
admin.site.register(Feedback)
