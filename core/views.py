from django.conf import settings
from django.contrib import messages
from django.db.models import Count, Sum
from django.shortcuts import get_object_or_404, redirect, render
import stripe

from blog.models import BlogPost
from events.models import Event
from .forms import ContactMessageForm, ExpertApplicationForm
from .models import Banner, Donation
from recovery.models import PatientProfile
from service.models import ExpertProfile, ServiceInquiry, ServiceType
from user.models import CustomUser

# Create your views here.

def home(request):
    # Get featured posts for the homepage
    featured_posts = BlogPost.objects.filter(
        status='published',
        is_featured=True
    ).select_related('author', 'category').order_by('-created_at')[:3]

    recent_posts = BlogPost.objects.filter(
        status='published'
    ).select_related('author', 'category').order_by('-created_at')[:4]

    banners = Banner.objects.filter(is_active=True).order_by('-id')
    service_types = ServiceType.objects.filter(is_active=True).order_by('name')
    upcoming_events = Event.objects.filter(is_active=True).order_by('event_date')[:3]

    stats = {
        'members': CustomUser.objects.filter(is_active=True).count(),
        'experts': ExpertProfile.objects.count(),
        'recovery_profiles': PatientProfile.objects.count(),
        'service_requests': ServiceInquiry.objects.count(),
    }
    
    context = {
        'featured_posts': featured_posts,
        'recent_posts': recent_posts,
        'banners': banners,
        'service_types': service_types,
        'upcoming_events': upcoming_events,
        'stats': stats,
    }
    return render(request, 'pages/home.html', context)

def about(request):
    return render(request, 'pages/about.html')

def how_it_works(request):
    return render(request, 'pages/how_it_works.html')

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

def rehab_center(request):
    return render(request, 'pages/rehab_center.html')

def baby_care_center(request):
    return render(request, 'pages/baby_care_center.html')

def save_daily_entry(request):
    # Placeholder view for saving daily entry
    return render(request, 'pages/recovery_tracking.html')


def contact_page(request):
    if request.method == 'POST':
        form = ContactMessageForm(request.POST)
        if form.is_valid():
            form.save()
            return render(request, 'pages/contact.html', {'form': ContactMessageForm(), 'submitted': True})
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'full_name': request.user.get_full_name(),
                'email': request.user.email,
            }
        form = ContactMessageForm(initial=initial)

    return render(request, 'pages/contact.html', {'form': form})


def become_expert(request):
    if request.method == 'POST':
        form = ExpertApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return render(request, 'pages/become_expert.html', {'form': ExpertApplicationForm(), 'submitted': True})
    else:
        initial = {}
        if request.user.is_authenticated:
            initial = {
                'full_name': request.user.get_full_name(),
                'email': request.user.email,
                'phone_number': getattr(request.user, 'phone_number', ''),
            }
        form = ExpertApplicationForm(initial=initial)
    return render(request, 'pages/become_expert.html', {'form': form})


def privacy_policy(request):
    return render(request, 'pages/privacy_policy.html')


def terms_of_service(request):
    return render(request, 'pages/terms_of_service.html')


def donate(request):
    return render(request, 'pages/donate.html', {
        'preset_amounts': [500, 1000, 2500, 5000, 10000],
    })


def donate_checkout(request):
    if request.method != 'POST':
        return redirect('donate')

    donor_name = request.POST.get('donor_name', '').strip()
    donor_email = request.POST.get('donor_email', '').strip()
    amount_str = request.POST.get('amount', '').strip()
    message = request.POST.get('message', '').strip()

    # Validate amount
    try:
        amount = float(amount_str)
        if amount < 10:
            raise ValueError
    except (ValueError, TypeError):
        messages.error(request, 'Please enter a valid amount (minimum ৳10).')
        return redirect('donate')

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[
                {
                    'price_data': {
                        'currency': 'bdt',
                        'product_data': {
                            'name': 'Donation to Novita',
                            'description': 'Your generous donation supports women empowerment and rehabilitation programs.',
                        },
                        'unit_amount': int(amount * 100),
                    },
                    'quantity': 1,
                }
            ],
            mode='payment',
            success_url=(
                request.build_absolute_uri('/donate/success/?session_id=')
                + '{CHECKOUT_SESSION_ID}'
            ),
            cancel_url=request.build_absolute_uri('/donate/'),
            customer_email=donor_email or None,
            metadata={
                'donor_name': donor_name,
                'donor_email': donor_email,
                'donor_message': message,
                'amount': str(amount),
            },
        )

        # Store pending donation
        Donation.objects.create(
            donor_name=donor_name or 'Anonymous',
            donor_email=donor_email,
            amount=amount,
            message=message,
            stripe_session_id=checkout_session.id,
            is_confirmed=False,
        )

        return redirect(checkout_session.url, code=303)
    except stripe.error.StripeError as e:
        messages.error(request, f'Payment error: {str(e)}')
        return redirect('donate')


def donate_success(request):
    session_id = request.GET.get('session_id', '')
    if not session_id:
        return redirect('donate')

    stripe.api_key = settings.STRIPE_SECRET_KEY
    try:
        session = stripe.checkout.Session.retrieve(session_id)
        if session.payment_status == 'paid':
            Donation.objects.filter(stripe_session_id=session_id).update(is_confirmed=True)
            messages.success(request, 'Thank you! Your donation has been received.')
    except stripe.error.StripeError:
        pass

    # Aggregate confirmed donation stats
    stats = Donation.objects.filter(is_confirmed=True).aggregate(
        total_amount=Sum('amount'),
        total_count=Count('id'),
    )
    return render(request, 'pages/donate_success.html', {'stats': stats})
