from django.db import models
from django.utils import timezone
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator

User = settings.AUTH_USER_MODEL


class PatientProfile(models.Model):
    ADDICTION_CHOICES = [
        ('alcohol', 'Alcohol'),
        ('opioids', 'Opioids / Heroin'),
        ('stimulants', 'Stimulants (Cocaine, Meth)'),
        ('cannabis', 'Cannabis / Marijuana'),
        ('prescription', 'Prescription Drugs'),
        ('tobacco', 'Tobacco / Nicotine'),
        ('gambling', 'Gambling'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('active', 'Active'),
        ('on_hold', 'On Hold'),
        ('completed', 'Completed'),
        ('discharged', 'Discharged'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='patient_profile')
    addiction_type = models.CharField(max_length=20, choices=ADDICTION_CHOICES)
    program_start_date = models.DateField(default=timezone.now)
    assigned_counselor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='counselor_patients',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    rehab_center = models.CharField(max_length=200, blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=15, blank=True)
    emergency_contact_relation = models.CharField(max_length=50, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        name = self.user.full_name or self.user.email
        return f"{name} — {self.get_addiction_type_display()}"

    @property
    def days_clean(self):
        last_relapse = self.relapses.order_by('-date').first()
        start = last_relapse.date if last_relapse else self.program_start_date
        return max((timezone.now().date() - start).days, 0)

    @property
    def total_checkins(self):
        return self.checkins.count()

    @property
    def achieved_milestones_count(self):
        return self.milestones.filter(is_achieved=True).count()

    class Meta:
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'


class RecoveryPlan(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('completed', 'Completed'),
        ('revised', 'Revised'),
        ('on_hold', 'On Hold'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='plans')
    title = models.CharField(max_length=200)
    short_term_goals = models.TextField()
    long_term_goals = models.TextField()
    strategies = models.TextField()
    start_date = models.DateField(default=timezone.now)
    review_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    created_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='created_plans'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.title} — {self.patient}"

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Recovery Plan'


class DailyCheckIn(models.Model):
    MOOD_CHOICES = [
        (1, 'Very Bad 😞'),
        (2, 'Bad 😔'),
        (3, 'Okay 😐'),
        (4, 'Good 😊'),
        (5, 'Excellent 😄'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='checkins')
    date = models.DateField(default=timezone.now)
    mood = models.IntegerField(
        choices=MOOD_CHOICES,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
    )
    craving_level = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(10)],
        help_text='Scale 1–10 (1 = minimal, 10 = severe)',
    )
    used_substance = models.BooleanField(default=False)
    sleep_hours = models.DecimalField(max_digits=4, decimal_places=1, null=True, blank=True)
    exercise_done = models.BooleanField(default=False)
    trigger_avoided = models.BooleanField(default=False)
    support_used = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        unique_together = ['patient', 'date']
        verbose_name = 'Daily Check-In'

    def __str__(self):
        return f"Check-in {self.date} — {self.patient.user.email}"

    def get_mood_emoji(self):
        emojis = {1: '😞', 2: '😔', 3: '😐', 4: '😊', 5: '😄'}
        return emojis.get(self.mood, '😐')


class CounselingSession(models.Model):
    SESSION_TYPE_CHOICES = [
        ('individual', 'Individual'),
        ('group', 'Group'),
        ('family', 'Family'),
        ('online', 'Online / Telehealth'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='sessions')
    counselor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, related_name='conducted_sessions'
    )
    session_date = models.DateField()
    session_time = models.TimeField()
    session_type = models.CharField(max_length=20, choices=SESSION_TYPE_CHOICES, default='individual')
    duration_minutes = models.IntegerField(default=60)
    topics_discussed = models.TextField()
    counselor_notes = models.TextField(blank=True)
    patient_feedback = models.TextField(blank=True)
    homework = models.TextField(blank=True, help_text='Tasks assigned to the patient')
    next_session_date = models.DateField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-session_date', '-session_time']
        verbose_name = 'Counseling Session'

    def __str__(self):
        return f"Session {self.session_date} — {self.patient}"


class RelapseRecord(models.Model):
    SEVERITY_CHOICES = [
        ('mild', 'Mild'),
        ('moderate', 'Moderate'),
        ('severe', 'Severe'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='relapses')
    date = models.DateField()
    substance = models.CharField(max_length=100)
    trigger = models.TextField()
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES)
    duration = models.CharField(max_length=100, blank=True, help_text='e.g. 2 hours, 1 day')
    support_received = models.BooleanField(default=False)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date']
        verbose_name = 'Relapse Record'

    def __str__(self):
        return f"Relapse {self.date} — {self.patient}"


MILESTONE_DAY_TARGETS = [7, 14, 30, 60, 90, 180, 365]


class Milestone(models.Model):
    MILESTONE_TYPE_CHOICES = [
        ('days_clean', 'Days Clean'),
        ('goal_achieved', 'Goal Achieved'),
        ('program_stage', 'Program Stage'),
        ('custom', 'Custom'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='milestones')
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    milestone_type = models.CharField(
        max_length=20, choices=MILESTONE_TYPE_CHOICES, default='days_clean'
    )
    target_days = models.IntegerField(null=True, blank=True)
    achieved_date = models.DateField(null=True, blank=True)
    is_achieved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['target_days', '-created_at']
        verbose_name = 'Milestone'

    def __str__(self):
        status = '✓' if self.is_achieved else '○'
        return f"[{status}] {self.title}"


class Appointment(models.Model):
    APPOINTMENT_TYPE_CHOICES = [
        ('counseling', 'Counseling Session'),
        ('medical', 'Medical Check-up'),
        ('group', 'Group Session'),
        ('follow_up', 'Follow-up'),
        ('intake', 'Intake Assessment'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('missed', 'Missed'),
        ('rescheduled', 'Rescheduled'),
    ]

    patient = models.ForeignKey(PatientProfile, on_delete=models.CASCADE, related_name='appointments')
    counselor = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        related_name='patient_appointments',
    )
    title = models.CharField(max_length=200)
    appointment_type = models.CharField(
        max_length=20, choices=APPOINTMENT_TYPE_CHOICES, default='counseling'
    )
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    location = models.CharField(max_length=200, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['appointment_date', 'appointment_time']
        verbose_name = 'Appointment'

    def __str__(self):
        return f"{self.title} — {self.appointment_date}"

    @property
    def is_upcoming(self):
        return (
            self.appointment_date >= timezone.now().date()
            and self.status == 'scheduled'
        )
