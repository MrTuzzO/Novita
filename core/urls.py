from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('recovery-tracking/', views.recovery_tracking, name='recovery_tracking'),
    
    # Additional recovery tracking URLs
    path('recovery-history/', views.recovery_history, name='recovery_history'),
    path('export-data/', views.export_data, name='export_data'),
    path('set-goals/', views.set_goals, name='set_goals'),
    
    # Support Groups and Community
    path('groups/', views.groups_view, name='groups'),
    path('mentors/', views.mentors_view, name='mentors'),
    path('milestones/', views.milestones_view, name='milestones'),
    path('appointments/', views.appointments_view, name='appointments'),
    path('rehab-center/', views.rehab_center, name='rehab_center'),
    path('baby-care-center/', views.baby_care_center, name='baby_care_center'),
    path('save-daily-entry/', views.save_daily_entry, name='save_daily_entry'),
]