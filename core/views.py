from django.shortcuts import render
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from django.urls import reverse_lazy

# Create your views here.

def home(request):
    return render(request, 'pages/home.html')

def about(request):
    return render(request, 'pages/about.html')

def how_it_works(request):
    return render(request, 'pages/how_it_works.html')

def resources(request):
    return render(request, 'pages/resources.html')

def dashboard(request):
    return render(request, 'pages/dashboard.html')

def recovery_tracking(request):
    # Sample data for the recovery tracking page
    context = {
        'mood_choices': [
            ('1', 'Very Bad'),
            ('2', 'Bad'),
            ('3', 'Okay'),
            ('4', 'Good'),
            ('5', 'Very Good'),
        ],
        'streak_data': {
            'days_sober': 15,
            'recovery_progress': 68,
            'milestones_achieved': 3,
        },
        'recent_entries': [],  # Empty for now
        'next_milestone': {
            'days': 30,
            'title': '30 Days Milestone',
            'progress': 50,
            'days_remaining': 15,
        },
        'mood_labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'mood_data': [7, 8, 6, 9, 7, 8, 9],
        'cravings_labels': ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'],
        'cravings_data': [3, 2, 4, 1, 2, 1, 1],
    }
    return render(request, 'pages/recovery_tracking.html', context)

def login_view(request):
    return render(request, 'pages/login.html')

def signup_view(request):
    return render(request, 'pages/signup.html')

# Placeholder views for URLs referenced in recovery_tracking.html
def recovery_history(request):
    return render(request, 'pages/recovery_tracking.html')  # Redirect to main tracking for now

def export_data(request):
    # Placeholder - would handle data export
    return render(request, 'pages/recovery_tracking.html')

def set_goals(request):
    # Placeholder - would handle goal setting
    return render(request, 'pages/recovery_tracking.html')

# Custom Password Reset Views
class CustomPasswordResetView(PasswordResetView):
    template_name = 'pages/password_reset.html'
    success_url = reverse_lazy('password_reset_done')
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'

class CustomPasswordResetDoneView(PasswordResetDoneView):
    template_name = 'pages/password_reset_done.html'

class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = 'pages/password_reset_confirm.html'
    success_url = reverse_lazy('password_reset_complete')

class CustomPasswordResetCompleteView(PasswordResetCompleteView):
    template_name = 'pages/password_reset_complete.html'
