from django.urls import path
from . import views

app_name = 'recovery'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),

    # Patient Profile
    path('profile/setup/', views.setup_profile, name='setup_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),

    # Recovery Plans
    path('plans/', views.plan_list, name='plan_list'),
    path('plans/create/', views.plan_create, name='plan_create'),
    path('plans/<int:pk>/', views.plan_detail, name='plan_detail'),
    path('plans/<int:pk>/edit/', views.plan_edit, name='plan_edit'),

    # Daily Check-In
    path('checkin/', views.checkin_create, name='checkin_create'),
    path('checkin/history/', views.checkin_history, name='checkin_history'),

    # Counseling Sessions
    path('sessions/', views.session_list, name='session_list'),
    path('sessions/log/', views.session_log, name='session_log'),

    # Relapse Records
    path('relapses/', views.relapse_list, name='relapse_list'),
    path('relapses/log/', views.relapse_log, name='relapse_log'),

    # Milestones
    path('milestones/', views.milestones_view, name='milestones'),
    path('milestones/<int:pk>/achieve/', views.milestone_achieve, name='milestone_achieve'),

    # Appointments
    path('appointments/', views.appointment_list, name='appointments'),
    path('appointments/book/', views.appointment_create, name='appointment_create'),
    path('appointments/<int:pk>/cancel/', views.appointment_cancel, name='appointment_cancel'),

    # Staff / Admin views
    path('analytics/', views.analytics, name='analytics'),
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/<int:pk>/', views.patient_detail, name='patient_detail'),
]
