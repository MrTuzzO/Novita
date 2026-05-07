from django import forms
from .models import (
    PatientProfile, RecoveryPlan, DailyCheckIn,
    CounselingSession, RelapseRecord, Milestone, Appointment,
)

INPUT_CLASS = (
    'w-full rounded-xl border border-slate-300 px-4 py-2.5 text-sm '
    'text-slate-800 focus:border-[var(--color-primary)] focus:outline-none focus:ring-2 '
    'focus:ring-[var(--color-primary)]/20'
)
TEXTAREA_CLASS = INPUT_CLASS + ' resize-none'
SELECT_CLASS = INPUT_CLASS


class PatientProfileSetupForm(forms.ModelForm):
    """Used on the initial profile setup page (no admin-level fields)."""
    class Meta:
        model = PatientProfile
        fields = [
            'addiction_type', 'program_start_date', 'rehab_center', 'notes',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
        ]
        widgets = {
            'addiction_type': forms.Select(attrs={'class': SELECT_CLASS}),
            'program_start_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'rehab_center': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Rehab center name (optional)'}),
            'notes': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3, 'placeholder': 'Additional notes…'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Full name'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '+60 123 456 789'}),
            'emergency_contact_relation': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. Mother, Friend'}),
        }


class PatientProfileForm(forms.ModelForm):
    """Used on the edit profile page (includes admin-level fields)."""
    class Meta:
        model = PatientProfile
        fields = [
            'addiction_type', 'program_start_date', 'status', 'rehab_center',
            'assigned_counselor', 'notes',
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation',
        ]
        widgets = {
            'addiction_type': forms.Select(attrs={'class': SELECT_CLASS}),
            'program_start_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
            'rehab_center': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Rehab center name (optional)'}),
            'assigned_counselor': forms.Select(attrs={'class': SELECT_CLASS}),
            'notes': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3, 'placeholder': 'Additional notes…'}),
            'emergency_contact_name': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Full name'}),
            'emergency_contact_phone': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': '+60 123 456 789'}),
            'emergency_contact_relation': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. Mother, Friend'}),
        }


class RecoveryPlanForm(forms.ModelForm):
    class Meta:
        model = RecoveryPlan
        fields = ['title', 'short_term_goals', 'long_term_goals', 'strategies', 'start_date', 'review_date', 'status']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Plan title'}),
            'short_term_goals': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3, 'placeholder': 'Goals for the next 30 days…'}),
            'long_term_goals': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3, 'placeholder': 'Goals for the next 6–12 months…'}),
            'strategies': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 4, 'placeholder': 'Coping strategies, support resources, action steps…'}),
            'start_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'review_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'status': forms.Select(attrs={'class': SELECT_CLASS}),
        }


class DailyCheckInForm(forms.ModelForm):
    class Meta:
        model = DailyCheckIn
        fields = [
            'date', 'mood', 'craving_level', 'used_substance',
            'sleep_hours', 'exercise_done', 'trigger_avoided', 'support_used', 'notes',
        ]
        widgets = {
            'date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'mood': forms.Select(attrs={'class': SELECT_CLASS}),
            'craving_level': forms.NumberInput(attrs={
                'class': INPUT_CLASS, 'min': 1, 'max': 10, 'type': 'range',
                'oninput': 'document.getElementById("craving_display").textContent = this.value',
            }),
            'sleep_hours': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': 0, 'max': 24, 'step': '0.5', 'placeholder': '7.5'}),
            'notes': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3, 'placeholder': 'How was your day? Any challenges or wins?'}),
            'used_substance': forms.CheckboxInput(attrs={'class': 'rounded border-slate-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)]'}),
            'exercise_done': forms.CheckboxInput(attrs={'class': 'rounded border-slate-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)]'}),
            'trigger_avoided': forms.CheckboxInput(attrs={'class': 'rounded border-slate-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)]'}),
            'support_used': forms.CheckboxInput(attrs={'class': 'rounded border-slate-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)]'}),
        }


class CounselingSessionForm(forms.ModelForm):
    class Meta:
        model = CounselingSession
        fields = [
            'session_date', 'session_time', 'session_type', 'duration_minutes',
            'topics_discussed', 'counselor_notes', 'patient_feedback', 'homework', 'next_session_date',
        ]
        widgets = {
            'session_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'session_time': forms.TimeInput(attrs={'class': INPUT_CLASS, 'type': 'time'}),
            'session_type': forms.Select(attrs={'class': SELECT_CLASS}),
            'duration_minutes': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': 15, 'placeholder': '60'}),
            'topics_discussed': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3, 'placeholder': 'Key topics covered…'}),
            'counselor_notes': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 3, 'placeholder': 'Clinical observations and notes…'}),
            'patient_feedback': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 2, 'placeholder': 'Patient\'s feedback or comments…'}),
            'homework': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 2, 'placeholder': 'Tasks assigned before next session…'}),
            'next_session_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
        }


class RelapseRecordForm(forms.ModelForm):
    class Meta:
        model = RelapseRecord
        fields = ['date', 'substance', 'trigger', 'severity', 'duration', 'support_received', 'notes']
        widgets = {
            'date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'substance': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. Alcohol, Opioids'}),
            'trigger': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 2, 'placeholder': 'What triggered the relapse?'}),
            'severity': forms.Select(attrs={'class': SELECT_CLASS}),
            'duration': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. 2 hours, 1 day'}),
            'support_received': forms.CheckboxInput(attrs={'class': 'rounded border-slate-300 text-[var(--color-primary)] focus:ring-[var(--color-primary)]'}),
            'notes': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 2, 'placeholder': 'Additional context or how you recovered…'}),
        }


class MilestoneForm(forms.ModelForm):
    class Meta:
        model = Milestone
        fields = ['title', 'description', 'milestone_type', 'target_days']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. 30 Days Clean'}),
            'description': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 2, 'placeholder': 'What does this milestone mean to you?'}),
            'milestone_type': forms.Select(attrs={'class': SELECT_CLASS}),
            'target_days': forms.NumberInput(attrs={'class': INPUT_CLASS, 'min': 1, 'placeholder': 'e.g. 30'}),
        }


class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['title', 'appointment_type', 'appointment_date', 'appointment_time', 'counselor', 'location', 'notes']
        widgets = {
            'title': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'Appointment title'}),
            'appointment_type': forms.Select(attrs={'class': SELECT_CLASS}),
            'appointment_date': forms.DateInput(attrs={'class': INPUT_CLASS, 'type': 'date'}),
            'appointment_time': forms.TimeInput(attrs={'class': INPUT_CLASS, 'type': 'time'}),
            'counselor': forms.Select(attrs={'class': SELECT_CLASS}),
            'location': forms.TextInput(attrs={'class': INPUT_CLASS, 'placeholder': 'e.g. Room 3, Telehealth'}),
            'notes': forms.Textarea(attrs={'class': TEXTAREA_CLASS, 'rows': 2, 'placeholder': 'Any special notes for this appointment…'}),
        }
