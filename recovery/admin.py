from django.contrib import admin
from .models import (
    PatientProfile, RecoveryPlan, DailyCheckIn,
    CounselingSession, RelapseRecord, Milestone, Appointment,
)


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'addiction_type', 'status', 'program_start_date', 'days_clean', 'assigned_counselor')
    list_filter = ('status', 'addiction_type')
    search_fields = ('user__email', 'user__full_name', 'rehab_center')
    readonly_fields = ('days_clean', 'total_checkins', 'achieved_milestones_count', 'created_at', 'updated_at')
    fieldsets = (
        ('Patient', {'fields': ('user', 'addiction_type', 'status', 'program_start_date', 'rehab_center', 'assigned_counselor', 'notes')}),
        ('Emergency Contact', {'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation')}),
        ('Stats (read-only)', {'fields': ('days_clean', 'total_checkins', 'achieved_milestones_count')}),
        ('Timestamps', {'fields': ('created_at', 'updated_at'), 'classes': ('collapse',)}),
    )


@admin.register(RecoveryPlan)
class RecoveryPlanAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'status', 'start_date', 'review_date', 'created_by')
    list_filter = ('status',)
    search_fields = ('title', 'patient__user__email')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(DailyCheckIn)
class DailyCheckInAdmin(admin.ModelAdmin):
    list_display = ('patient', 'date', 'mood', 'craving_level', 'used_substance', 'exercise_done')
    list_filter = ('mood', 'used_substance', 'exercise_done')
    search_fields = ('patient__user__email',)
    date_hierarchy = 'date'


@admin.register(CounselingSession)
class CounselingSessionAdmin(admin.ModelAdmin):
    list_display = ('patient', 'counselor', 'session_date', 'session_type', 'duration_minutes')
    list_filter = ('session_type',)
    search_fields = ('patient__user__email', 'counselor__email')
    date_hierarchy = 'session_date'


@admin.register(RelapseRecord)
class RelapseRecordAdmin(admin.ModelAdmin):
    list_display = ('patient', 'date', 'substance', 'severity', 'support_received')
    list_filter = ('severity', 'support_received')
    search_fields = ('patient__user__email', 'substance')
    date_hierarchy = 'date'


@admin.register(Milestone)
class MilestoneAdmin(admin.ModelAdmin):
    list_display = ('patient', 'title', 'milestone_type', 'target_days', 'is_achieved', 'achieved_date')
    list_filter = ('is_achieved', 'milestone_type')
    search_fields = ('patient__user__email', 'title')


@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('title', 'patient', 'counselor', 'appointment_date', 'appointment_time', 'status', 'appointment_type')
    list_filter = ('status', 'appointment_type')
    search_fields = ('patient__user__email', 'title')
    date_hierarchy = 'appointment_date'
