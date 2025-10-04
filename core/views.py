from django.shortcuts import render
from blog.models import BlogPost

# Create your views here.

def home(request):
    # Get featured posts for the homepage
    featured_posts = BlogPost.objects.filter(
        status='published',
        is_featured=True
    ).select_related('author', 'category').order_by('-created_at')[:3]
    
    context = {
        'featured_posts': featured_posts,
    }
    return render(request, 'pages/home.html', context)

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

# Placeholder views for URLs referenced in recovery_tracking.html
def recovery_history(request):
    return render(request, 'pages/recovery_tracking.html')  # Redirect to main tracking for now

def export_data(request):
    # Placeholder - would handle data export
    return render(request, 'pages/recovery_tracking.html')

def set_goals(request):
    # Placeholder - would handle goal setting
    return render(request, 'pages/recovery_tracking.html')

def groups_view(request):
    # Placeholder view for support groups
    return render(request, 'pages/groups.html')

def mentors_view(request):
    # Placeholder view for mentors
    return render(request, 'pages/mentors.html')

def milestones_view(request):
    # Placeholder view for milestones
    return render(request, 'pages/milestones.html')

def appointments_view(request):
    # Placeholder view for appointments
    return render(request, 'pages/appointments.html')

def save_daily_entry(request):
    # Placeholder view for saving daily entry
    return render(request, 'pages/recovery_tracking.html')
