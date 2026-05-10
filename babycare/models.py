import random
import string

from django.conf import settings
from django.db import models


class BabyCareRequest(models.Model):
    STATUS_SUBMITTED = 'submitted'
    STATUS_VISIT_SCHEDULED = 'visit_scheduled'
    STATUS_WAITLISTED = 'waitlisted'
    STATUS_ENROLLED = 'enrolled'
    STATUS_ACTIVE = 'active'
    STATUS_CLOSED = 'closed'

    SHIFT_FULL_DAY = 'full_day'
    SHIFT_HALF_DAY = 'half_day'
    SHIFT_HOURLY = 'hourly'
    SHIFT_CHOICES = [
        (SHIFT_FULL_DAY, 'Full Day'),
        (SHIFT_HALF_DAY, 'Half Day'),
        (SHIFT_HOURLY, 'Hourly'),
    ]

    STATUS_CHOICES = [
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_VISIT_SCHEDULED, 'Visit Scheduled'),
        (STATUS_WAITLISTED, 'Waitlisted'),
        (STATUS_ENROLLED, 'Enrolled'),
        (STATUS_ACTIVE, 'Active Day Care'),
        (STATUS_CLOSED, 'Closed'),
    ]

    request_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='baby_care_requests',
    )
    parent_full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    child_name = models.CharField(max_length=120)
    child_age_years = models.PositiveSmallIntegerField(null=True, blank=True)
    care_shift = models.CharField(max_length=20, choices=SHIFT_CHOICES, default=SHIFT_FULL_DAY)
    care_requirements = models.TextField(help_text='Mention food preference, nap routine, allergies, and special support needs.')
    preferred_start_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.request_id} - {self.parent_full_name}'

    def save(self, *args, **kwargs):
        if not self.request_id:
            while True:
                candidate = 'BC' + ''.join(random.choices(string.digits, k=8))
                if not BabyCareRequest.objects.filter(request_id=candidate).exists():
                    self.request_id = candidate
                    break
        super().save(*args, **kwargs)


class BabyCareUpdate(models.Model):
    care_request = models.ForeignKey(
        BabyCareRequest,
        on_delete=models.CASCADE,
        related_name='updates',
    )
    note = models.TextField()
    is_visible_to_parent = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='baby_care_updates',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Update for {self.care_request.request_id}'
