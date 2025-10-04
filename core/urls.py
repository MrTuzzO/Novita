from django.urls import path
from . import views

urlpatterns = [
    # Main pages
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('how-it-works/', views.how_it_works, name='how_it_works'),
    path('resources/', views.resources, name='resources'),
    
    # Dashboard and tracking
    path('dashboard/', views.dashboard, name='dashboard'),
    path('recovery-tracking/', views.recovery_tracking, name='recovery_tracking'),
    
    # Authentication
    path('login/', views.login_view, name='login'),
    path('signup/', views.signup_view, name='signup'),
    
    # Password Reset URLs
    path('password-reset/', views.CustomPasswordResetView.as_view(), name='password_reset'),
    path('password-reset/done/', views.CustomPasswordResetDoneView.as_view(), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', views.CustomPasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('password-reset/complete/', views.CustomPasswordResetCompleteView.as_view(), name='password_reset_complete'),
    
    # Additional recovery tracking URLs
    path('recovery-history/', views.recovery_history, name='recovery_history'),
    path('export-data/', views.export_data, name='export_data'),
    path('set-goals/', views.set_goals, name='set_goals'),
]