from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Avg, Count, Q

from .models import (
    PatientProfile, RecoveryPlan, DailyCheckIn,
    CounselingSession, RelapseRecord, Milestone, Appointment,
    MILESTONE_DAY_TARGETS,
)
from .forms import (
    PatientProfileForm, PatientProfileSetupForm, RecoveryPlanForm, DailyCheckInForm,
    CounselingSessionForm, RelapseRecordForm, MilestoneForm, AppointmentForm,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _get_patient_or_none(user):
    try:
        return user.patient_profile
    except PatientProfile.DoesNotExist:
        return None


def _auto_award_milestones(patient):
    """Award days-clean milestones automatically based on current streak."""
    days = patient.days_clean
    for target in MILESTONE_DAY_TARGETS:
        if days >= target:
            Milestone.objects.get_or_create(
                patient=patient,
                milestone_type='days_clean',
                target_days=target,
                defaults={
                    'title': f'{target} Days Clean',
                    'description': f'You have stayed clean for {target} consecutive days. Outstanding!',
                    'is_achieved': True,
                    'achieved_date': timezone.now().date(),
                },
            )


# ---------------------------------------------------------------------------
# Dashboard
# ---------------------------------------------------------------------------

@login_required
def dashboard(request):
    patient = _get_patient_or_none(request.user)
    if not patient:
        messages.info(request, 'Please complete your recovery profile to get started.')
        return redirect('recovery:setup_profile')

    _auto_award_milestones(patient)

    today = timezone.now().date()
    todays_checkin = patient.checkins.filter(date=today).first()
    recent_checkins = list(patient.checkins.order_by('-date')[:7])
    upcoming_appointments = patient.appointments.filter(
        appointment_date__gte=today, status='scheduled'
    ).order_by('appointment_date', 'appointment_time')[:5]
    recent_sessions = patient.sessions.order_by('-session_date')[:3]
    active_plan = patient.plans.filter(status='active').first()
    milestones = patient.milestones.order_by('target_days')
    recent_relapses = patient.relapses.order_by('-date')[:3]

    mood_data = [c.mood for c in reversed(recent_checkins)]
    craving_data = [c.craving_level for c in reversed(recent_checkins)]
    checkin_dates = [str(c.date) for c in reversed(recent_checkins)]

    next_milestone = None
    days = patient.days_clean
    for target in MILESTONE_DAY_TARGETS:
        if days < target:
            next_milestone = {
                'title': f'{target} Days Clean',
                'target_days': target,
                'days_remaining': target - days,
                'progress': round((days / target) * 100),
            }
            break

    context = {
        'patient': patient,
        'todays_checkin': todays_checkin,
        'recent_checkins': recent_checkins,
        'upcoming_appointments': upcoming_appointments,
        'recent_sessions': recent_sessions,
        'active_plan': active_plan,
        'milestones': milestones,
        'recent_relapses': recent_relapses,
        'next_milestone': next_milestone,
        'mood_data': mood_data,
        'craving_data': craving_data,
        'checkin_dates': checkin_dates,
    }
    return render(request, 'recovery/dashboard.html', context)


# ---------------------------------------------------------------------------
# Patient Profile
# ---------------------------------------------------------------------------

@login_required
def setup_profile(request):
    if _get_patient_or_none(request.user):
        return redirect('recovery:dashboard')

    if request.method == 'POST':
        form = PatientProfileSetupForm(request.POST)
        if form.is_valid():
            profile = form.save(commit=False)
            profile.user = request.user
            profile.status = 'active'
            profile.save()
            _auto_award_milestones(profile)
            messages.success(request, 'Recovery profile created! Welcome to your recovery journey.')
            return redirect('recovery:dashboard')
    else:
        form = PatientProfileSetupForm()

    return render(request, 'recovery/profile_setup.html', {'form': form})


@login_required
def edit_profile(request):
    patient = get_object_or_404(PatientProfile, user=request.user)

    if request.method == 'POST':
        form = PatientProfileForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('recovery:dashboard')
    else:
        form = PatientProfileForm(instance=patient)

    return render(request, 'recovery/profile_edit.html', {'form': form, 'patient': patient})


# ---------------------------------------------------------------------------
# Recovery Plan
# ---------------------------------------------------------------------------

@login_required
def plan_list(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    plans = patient.plans.all()
    return render(request, 'recovery/plan_list.html', {'plans': plans, 'patient': patient})


@login_required
def plan_create(request):
    patient = get_object_or_404(PatientProfile, user=request.user)

    if request.method == 'POST':
        form = RecoveryPlanForm(request.POST)
        if form.is_valid():
            plan = form.save(commit=False)
            plan.patient = patient
            plan.created_by = request.user
            plan.save()
            messages.success(request, 'Recovery plan created.')
            return redirect('recovery:plan_list')
    else:
        form = RecoveryPlanForm()

    return render(request, 'recovery/plan_form.html', {'form': form, 'title': 'Create Recovery Plan'})


@login_required
def plan_detail(request, pk):
    patient = get_object_or_404(PatientProfile, user=request.user)
    plan = get_object_or_404(RecoveryPlan, pk=pk, patient=patient)
    return render(request, 'recovery/plan_detail.html', {'plan': plan, 'patient': patient})


@login_required
def plan_edit(request, pk):
    patient = get_object_or_404(PatientProfile, user=request.user)
    plan = get_object_or_404(RecoveryPlan, pk=pk, patient=patient)

    if request.method == 'POST':
        form = RecoveryPlanForm(request.POST, instance=plan)
        if form.is_valid():
            form.save()
            messages.success(request, 'Recovery plan updated.')
            return redirect('recovery:plan_detail', pk=plan.pk)
    else:
        form = RecoveryPlanForm(instance=plan)

    return render(request, 'recovery/plan_form.html', {'form': form, 'title': 'Edit Recovery Plan', 'plan': plan})


# ---------------------------------------------------------------------------
# Daily Check-In
# ---------------------------------------------------------------------------

@login_required
def checkin_create(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    today = timezone.now().date()

    existing = patient.checkins.filter(date=today).first()
    if existing:
        messages.info(request, "You've already checked in today.")
        return redirect('recovery:checkin_history')

    if request.method == 'POST':
        form = DailyCheckInForm(request.POST)
        if form.is_valid():
            checkin = form.save(commit=False)
            checkin.patient = patient
            checkin.save()
            _auto_award_milestones(patient)
            messages.success(request, 'Check-in saved! Keep it up.')
            return redirect('recovery:dashboard')
    else:
        form = DailyCheckInForm(initial={'date': today})

    return render(request, 'recovery/checkin_form.html', {'form': form, 'patient': patient})


@login_required
def checkin_history(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    checkins = patient.checkins.all()
    avg_mood = checkins.aggregate(avg=Avg('mood'))['avg']
    avg_craving = checkins.aggregate(avg=Avg('craving_level'))['avg']
    return render(request, 'recovery/checkin_history.html', {
        'checkins': checkins,
        'patient': patient,
        'avg_mood': round(avg_mood, 1) if avg_mood else None,
        'avg_craving': round(avg_craving, 1) if avg_craving else None,
    })


# ---------------------------------------------------------------------------
# Counseling Sessions
# ---------------------------------------------------------------------------

@login_required
def session_list(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    sessions = patient.sessions.select_related('counselor').all()
    return render(request, 'recovery/session_list.html', {'sessions': sessions, 'patient': patient})


@login_required
def session_log(request):
    """Counselors or admins log a session for a patient."""
    if request.user.role not in ('expert', 'admin'):
        messages.error(request, 'Only counselors can log sessions.')
        return redirect('recovery:dashboard')

    patient_id = request.GET.get('patient') or request.POST.get('patient_id')
    patient = get_object_or_404(PatientProfile, pk=patient_id) if patient_id else None

    if request.method == 'POST':
        form = CounselingSessionForm(request.POST)
        if form.is_valid():
            session = form.save(commit=False)
            session.patient = patient
            session.counselor = request.user
            session.save()
            messages.success(request, 'Session logged successfully.')
            return redirect('recovery:patient_detail', pk=patient.pk)
    else:
        form = CounselingSessionForm()

    return render(request, 'recovery/session_form.html', {'form': form, 'patient': patient})


# ---------------------------------------------------------------------------
# Relapse Records
# ---------------------------------------------------------------------------

@login_required
def relapse_list(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    relapses = patient.relapses.all()
    return render(request, 'recovery/relapse_list.html', {'relapses': relapses, 'patient': patient})


@login_required
def relapse_log(request):
    patient = get_object_or_404(PatientProfile, user=request.user)

    if request.method == 'POST':
        form = RelapseRecordForm(request.POST)
        if form.is_valid():
            relapse = form.save(commit=False)
            relapse.patient = patient
            relapse.save()
            messages.warning(request, 'Relapse recorded. Remember: recovery is a journey. Reach out for support.')
            return redirect('recovery:dashboard')
    else:
        form = RelapseRecordForm(initial={'date': timezone.now().date()})

    return render(request, 'recovery/relapse_form.html', {'form': form, 'patient': patient})


# ---------------------------------------------------------------------------
# Milestones
# ---------------------------------------------------------------------------

@login_required
def milestones_view(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    _auto_award_milestones(patient)

    if request.method == 'POST':
        form = MilestoneForm(request.POST)
        if form.is_valid():
            milestone = form.save(commit=False)
            milestone.patient = patient
            milestone.save()
            messages.success(request, 'Custom milestone added.')
            return redirect('recovery:milestones')
    else:
        form = MilestoneForm()

    milestones = patient.milestones.all()
    achieved = milestones.filter(is_achieved=True)
    pending = milestones.filter(is_achieved=False)

    return render(request, 'recovery/milestones.html', {
        'patient': patient,
        'milestones': milestones,
        'achieved': achieved,
        'pending': pending,
        'form': form,
        'day_targets': MILESTONE_DAY_TARGETS,
    })


@login_required
def milestone_achieve(request, pk):
    patient = get_object_or_404(PatientProfile, user=request.user)
    milestone = get_object_or_404(Milestone, pk=pk, patient=patient)
    milestone.is_achieved = True
    milestone.achieved_date = timezone.now().date()
    milestone.save()
    messages.success(request, f'Milestone "{milestone.title}" marked as achieved!')
    return redirect('recovery:milestones')


# ---------------------------------------------------------------------------
# Appointments
# ---------------------------------------------------------------------------

@login_required
def appointment_list(request):
    patient = get_object_or_404(PatientProfile, user=request.user)
    today = timezone.now().date()
    upcoming = patient.appointments.filter(appointment_date__gte=today).order_by('appointment_date', 'appointment_time')
    past = patient.appointments.filter(appointment_date__lt=today).order_by('-appointment_date')
    return render(request, 'recovery/appointment_list.html', {
        'upcoming': upcoming,
        'past': past,
        'patient': patient,
    })


@login_required
def appointment_create(request):
    patient = get_object_or_404(PatientProfile, user=request.user)

    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appt = form.save(commit=False)
            appt.patient = patient
            appt.save()
            messages.success(request, 'Appointment booked successfully.')
            return redirect('recovery:appointments')
    else:
        form = AppointmentForm()

    return render(request, 'recovery/appointment_form.html', {'form': form, 'patient': patient})


@login_required
def appointment_cancel(request, pk):
    patient = get_object_or_404(PatientProfile, user=request.user)
    appt = get_object_or_404(Appointment, pk=pk, patient=patient)
    appt.status = 'cancelled'
    appt.save()
    messages.info(request, 'Appointment cancelled.')
    return redirect('recovery:appointments')


# ---------------------------------------------------------------------------
# Analytics Dashboard (admin / counselor)
# ---------------------------------------------------------------------------

@login_required
def analytics(request):
    if request.user.role not in ('expert', 'admin'):
        messages.error(request, 'Access denied.')
        return redirect('recovery:dashboard')

    today = timezone.now().date()
    total_patients = PatientProfile.objects.count()
    active_patients = PatientProfile.objects.filter(status='active').count()
    total_checkins = DailyCheckIn.objects.count()
    relapses_this_month = RelapseRecord.objects.filter(
        date__year=today.year, date__month=today.month
    ).count()
    upcoming_appointments = Appointment.objects.filter(
        appointment_date__gte=today, status='scheduled'
    ).count()

    mood_trend = (
        DailyCheckIn.objects
        .filter(date__gte=today - timezone.timedelta(days=30))
        .values('date')
        .annotate(avg_mood=Avg('mood'))
        .order_by('date')
    )

    patients = PatientProfile.objects.select_related('user', 'assigned_counselor').order_by('-created_at')

    context = {
        'total_patients': total_patients,
        'active_patients': active_patients,
        'total_checkins': total_checkins,
        'relapses_this_month': relapses_this_month,
        'upcoming_appointments': upcoming_appointments,
        'mood_trend': list(mood_trend),
        'patients': patients,
    }
    return render(request, 'recovery/analytics.html', context)


# ---------------------------------------------------------------------------
# Patient management (counselor / admin)
# ---------------------------------------------------------------------------

@login_required
def patient_list(request):
    if request.user.role not in ('expert', 'admin'):
        messages.error(request, 'Access denied.')
        return redirect('recovery:dashboard')

    q = request.GET.get('q', '')
    patients = PatientProfile.objects.select_related('user', 'assigned_counselor').order_by('-created_at')
    if q:
        patients = patients.filter(
            Q(user__full_name__icontains=q) | Q(user__email__icontains=q)
        )

    return render(request, 'recovery/patient_list.html', {'patients': patients, 'q': q})


@login_required
def patient_detail(request, pk):
    if request.user.role not in ('expert', 'admin'):
        messages.error(request, 'Access denied.')
        return redirect('recovery:dashboard')

    patient = get_object_or_404(PatientProfile, pk=pk)
    checkins = patient.checkins.order_by('-date')[:10]
    sessions = patient.sessions.order_by('-session_date')[:5]
    relapses = patient.relapses.order_by('-date')[:5]
    appointments = patient.appointments.filter(
        appointment_date__gte=timezone.now().date()
    ).order_by('appointment_date')[:5]
    plans = patient.plans.filter(status='active')

    return render(request, 'recovery/patient_detail.html', {
        'patient': patient,
        'checkins': checkins,
        'sessions': sessions,
        'relapses': relapses,
        'appointments': appointments,
        'plans': plans,
    })
