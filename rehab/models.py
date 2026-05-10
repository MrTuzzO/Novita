import random
import string

from django.conf import settings
from django.db import models


class AdmissionRequest(models.Model):
    STATUS_SUBMITTED = 'submitted'
    STATUS_UNDER_REVIEW = 'under_review'
    STATUS_ACCEPTED = 'accepted'
    STATUS_WAITLISTED = 'waitlisted'
    STATUS_REJECTED = 'rejected'
    STATUS_ADMITTED = 'admitted'

    STATUS_CHOICES = [
        (STATUS_SUBMITTED, 'Submitted'),
        (STATUS_UNDER_REVIEW, 'Under Review'),
        (STATUS_ACCEPTED, 'Accepted'),
        (STATUS_WAITLISTED, 'Waitlisted'),
        (STATUS_REJECTED, 'Rejected'),
        (STATUS_ADMITTED, 'Admitted'),
    ]

    application_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='rehab_admission_requests',
    )
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20)
    age = models.PositiveSmallIntegerField(null=True, blank=True)
    primary_concern = models.TextField()
    preferred_admission_date = models.DateField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SUBMITTED)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.application_id} - {self.full_name}'

    def save(self, *args, **kwargs):
        if not self.application_id:
            while True:
                candidate = 'RA' + ''.join(random.choices(string.digits, k=8))
                if not AdmissionRequest.objects.filter(application_id=candidate).exists():
                    self.application_id = candidate
                    break
        super().save(*args, **kwargs)


class AdmissionUpdate(models.Model):
    admission_request = models.ForeignKey(
        AdmissionRequest,
        on_delete=models.CASCADE,
        related_name='updates',
    )
    note = models.TextField()
    is_visible_to_applicant = models.BooleanField(default=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='rehab_admission_updates',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Update for {self.admission_request.application_id}'
