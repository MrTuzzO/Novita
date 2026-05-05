from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
from django.utils import timezone


class ServiceType(models.Model):
    name = models.CharField(max_length=80, unique=True)
    slug = models.SlugField(max_length=80, unique=True)
    icon_class = models.CharField(max_length=60, default='fa-user-shield')
    short_description = models.CharField(max_length=180)
    details = models.TextField()
    how_it_works = models.TextField()
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['name']
        verbose_name = 'Service Type'
        verbose_name_plural = 'Service Types'

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('service:service_detail', kwargs={'slug': self.slug})


class ExpertProfile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='expert_profile',
    )
    title = models.CharField(max_length=120)
    bio = models.TextField()
    specialization = models.CharField(max_length=200, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    services = models.ManyToManyField(ServiceType, related_name='experts')
    profile_image = models.ImageField(upload_to='experts/', blank=True, null=True)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['user__full_name', 'user__email']
        verbose_name = 'Expert Profile'
        verbose_name_plural = 'Expert Profiles'

    def __str__(self):
        return self.display_name

    def clean(self):
        role = getattr(self.user, 'role', None)
        if role != 'expert':
            raise ValidationError({'user': 'Selected user must have Expert role.'})
        if not self.user.is_active:
            raise ValidationError({'user': 'Selected user account is inactive.'})

    @property
    def display_name(self):
        return self.user.get_full_name() or self.user.email


class ServiceInquiry(models.Model):
    STATUS_OPEN = 'open'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_WAITING_FOR_USER = 'waiting_for_user'
    STATUS_RESOLVED = 'resolved'
    STATUS_CLOSED = 'closed'

    STATUS_CHOICES = [
        (STATUS_OPEN, 'Open'),
        (STATUS_IN_PROGRESS, 'In Progress'),
        (STATUS_WAITING_FOR_USER, 'Waiting for User'),
        (STATUS_RESOLVED, 'Resolved'),
        (STATUS_CLOSED, 'Closed'),
    ]

    inquiry_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='service_inquiries')
    service_type = models.ForeignKey(ServiceType, on_delete=models.CASCADE, related_name='inquiries')
    expert = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_service_inquiries',
        limit_choices_to={'role': 'expert'},
    )
    subject = models.CharField(max_length=200)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_OPEN)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.inquiry_id} - {self.subject}'

    def save(self, *args, **kwargs):
        if not self.inquiry_id:
            import random
            import string
            while True:
                candidate = 'SV' + ''.join(random.choices(string.digits, k=8))
                if not ServiceInquiry.objects.filter(inquiry_id=candidate).exists():
                    self.inquiry_id = candidate
                    break

        if self.status == self.STATUS_CLOSED and not self.closed_at:
            self.closed_at = timezone.now()
        elif self.status != self.STATUS_CLOSED:
            self.closed_at = None
        super().save(*args, **kwargs)

    @property
    def is_open(self):
        return self.status in [self.STATUS_OPEN, self.STATUS_IN_PROGRESS, self.STATUS_WAITING_FOR_USER]


class ServiceMessage(models.Model):
    inquiry = models.ForeignKey(ServiceInquiry, on_delete=models.CASCADE, related_name='messages')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f'Message on {self.inquiry.inquiry_id}'

    @property
    def is_expert_message(self):
        return self.user == self.inquiry.expert


class ServiceMessageAttachment(models.Model):
    message = models.ForeignKey(ServiceMessage, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='service/attachments/%Y/%m/')
    original_filename = models.CharField(max_length=255)
    file_size = models.PositiveIntegerField(default=0)
    uploaded_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-uploaded_at']

    def save(self, *args, **kwargs):
        if self.file:
            self.original_filename = self.file.name
            self.file_size = self.file.size
        super().save(*args, **kwargs)

    @property
    def file_size_mb(self):
        return round(self.file_size / (1024 * 1024), 2)

    @property
    def is_image(self):
        lower = self.original_filename.lower()
        return lower.endswith('.jpg') or lower.endswith('.jpeg') or lower.endswith('.png') or lower.endswith('.gif') or lower.endswith('.webp')
