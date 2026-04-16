from django.urls import path
from . import views

urlpatterns = [
    path('',        views.home,        name='home'),
    path('login/',  views.user_login,  name='login'),
    path('logout/', views.user_logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # ── Admin ──────────────────────────────────────────────────────────────
    path('admin-panel/',                              views.admin_dashboard,        name='admin_dashboard'),

    # Workers
    path('admin-panel/workers/',                      views.admin_view_workers,     name='admin_view_workers'),
    path('admin-panel/workers/add/',                  views.admin_add_worker,       name='admin_add_worker'),
    path('admin-panel/workers/edit/<int:wid>/',       views.admin_edit_worker,      name='admin_edit_worker'),
    path('admin-panel/workers/toggle/<int:wid>/',     views.admin_toggle_worker,    name='admin_toggle_worker'),
    path('admin-panel/workers/delete/<int:wid>/',     views.admin_delete_worker,    name='admin_delete_worker'),

    # Police
    path('admin-panel/police/',                       views.admin_view_police,      name='admin_view_police'),
    path('admin-panel/police/add/',                   views.admin_add_police,       name='admin_add_police'),
    path('admin-panel/police/edit/<int:pid>/',        views.admin_edit_police,      name='admin_edit_police'),
    path('admin-panel/police/delete/<int:pid>/',      views.admin_delete_police,    name='admin_delete_police'),

    # Contractors
    path('admin-panel/contractors/',                  views.admin_view_contractors, name='admin_view_contractors'),
    path('admin-panel/contractors/add/',              views.admin_add_contractor,   name='admin_add_contractor'),
    path('admin-panel/contractors/edit/<int:rid>/',   views.admin_edit_contractor,  name='admin_edit_contractor'),
    path('admin-panel/contractors/delete/<int:rid>/', views.admin_delete_contractor,name='admin_delete_contractor'),

    # Other admin
    path('admin-panel/jobs/',       views.admin_view_jobs,       name='admin_view_jobs'),
    path('admin-panel/requests/',   views.admin_view_requests,   name='admin_view_requests'),
    path('admin-panel/insurance/',  views.admin_manage_insurance, name='admin_manage_insurance'),
    path('admin-panel/feedback/',   views.admin_view_feedback,   name='admin_view_feedback'),

    # ── Police ─────────────────────────────────────────────────────────────
    path('police/',                        views.police_dashboard,    name='police_dashboard'),
    path('police/workers/',                views.police_view_workers, name='police_view_workers'),
    path('police/workers/<int:wid>/noc/',  views.police_issue_noc,    name='police_issue_noc'),
    path('police/nocs/',                   views.police_view_nocs,    name='police_view_nocs'),

    # ── Employer ───────────────────────────────────────────────────────────
    path('employer/',                                     views.employer_dashboard,         name='employer_dashboard'),
    path('employer/jobs/',                                views.employer_view_jobs,         name='employer_view_jobs'),
    path('employer/jobs/add/',                            views.employer_add_job,           name='employer_add_job'),
    path('employer/applications/',                        views.employer_view_applications, name='employer_view_applications'),
    path('employer/applications/<int:rqid>/<str:action>/',views.employer_action_request,   name='employer_action_request'),
    path('employer/worker/<int:wid>/noc/',                views.employer_view_worker_noc,   name='employer_view_worker_noc'),

    # ── Worker ─────────────────────────────────────────────────────────────
    path('worker/',                        views.worker_dashboard,          name='worker_dashboard'),
    path('worker/profile/',                views.worker_profile,            name='worker_profile'),
    path('worker/noc/',                    views.worker_noc_status,         name='worker_noc_status'),
    path('worker/jobs/',                   views.worker_view_jobs,          name='worker_view_jobs'),
    path('worker/jobs/apply/<int:jid>/',   views.worker_apply_job,          name='worker_apply_job'),
    path('worker/applications/',           views.worker_application_status, name='worker_application_status'),
    path('worker/feedback/',               views.worker_feedback,           name='worker_feedback'),
]
