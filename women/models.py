from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.urls import reverse
import re
from django.utils.html import escape


class Course(models.Model):
    MODE_ONLINE = 'online'
    MODE_OFFLINE = 'offline'
    MODE_CHOICES = [
        (MODE_ONLINE, 'Online Course'),
        (MODE_OFFLINE, 'Offline Course'),
    ]

    title = models.CharField(max_length=180)
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default=MODE_ONLINE)
    short_description = models.CharField(max_length=220)
    description = models.TextField()
    thumbnail = models.ImageField(upload_to='women/courses/thumbnails/', blank=True, null=True)

    # Pricing
    fee = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text='Course fee in BDT. Leave as 0 for free courses.',
    )
    stripe_product_id = models.CharField(
        max_length=200,
        blank=True,
        help_text='Stripe Product ID for this course.',
    )

    # Offline-friendly fields (optional)
    location = models.CharField(max_length=180, blank=True)
    start_date = models.DateField(blank=True, null=True)
    duration_weeks = models.PositiveIntegerField(default=4)

    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['title']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('women:course_detail', kwargs={'course_id': self.id})


class CourseModule(models.Model):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='modules')
    title = models.CharField(max_length=180)
    summary = models.CharField(max_length=220, blank=True)
    order = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ['course', 'order', 'id']
        unique_together = ('course', 'order')

    def __str__(self):
        return f'{self.course.title} - Module {self.order}: {self.title}'


class ModuleLesson(models.Model):
    module = models.ForeignKey(CourseModule, on_delete=models.CASCADE, related_name='lessons')
    title = models.CharField(max_length=180)
    video_url = models.URLField(
        blank=True,
        help_text='Optional external video link (e.g., YouTube). You can also upload a video file below.',
    )
    video_file = models.FileField(
        upload_to='women/courses/videos/%Y/%m/',
        blank=True,
        null=True,
        help_text='Optional uploaded lesson video file.',
    )
    order = models.PositiveIntegerField(default=1)
    notes = models.TextField(blank=True)

    class Meta:
        ordering = ['module', 'order', 'id']
        unique_together = ('module', 'order')

    def __str__(self):
        return f'{self.module.title} - Lesson {self.order}: {self.title}'

    def clean(self):
        # Require at least one source, and disallow providing both to avoid ambiguity
        if not self.video_url and not self.video_file:
            raise ValidationError('Provide either a video URL or an uploaded video file.')
        if self.video_url and self.video_file:
            raise ValidationError('Please provide either a video URL or an uploaded file, not both.')

    def get_embed_url(self):
        """Return a canonical embed URL for known providers (YouTube, Vimeo) or None.

        This should be used directly in iframe src when available. We intentionally
        return None for unknown providers to avoid unsafe iframe usage.
        """
        if not self.video_url:
            return None
        # YouTube: capture 11-character id from common URL variants
        m = re.search(r'(?:v=|youtu\.be/|embed/)([A-Za-z0-9_-]{11})', self.video_url)
        if m:
            return f'https://www.youtube.com/embed/{escape(m.group(1))}'
        # Vimeo: numeric id
        m = re.search(r'vimeo\.com/(?:channels/.+/|groups/.+/videos/)?(\d+)', self.video_url)
        if m:
            return f'https://player.vimeo.com/video/{escape(m.group(1))}'
        return None


class Enrollment(models.Model):
    STATUS_PENDING = 'pending'  # For paid courses, waiting for payment
    STATUS_ACTIVE = 'active'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Payment'),
        (STATUS_ACTIVE, 'Active'),
        (STATUS_COMPLETED, 'Completed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='women_enrollments')
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name='enrollments')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_ACTIVE)
    enrolled_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(blank=True, null=True)
    
    # Payment tracking
    stripe_session_id = models.CharField(max_length=200, blank=True)
    payment_confirmed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('user', 'course')
        ordering = ['-enrolled_at']

    def __str__(self):
        return f'{self.user.email} - {self.course.title}'
    
    @property
    def is_paid(self):
        """Check if enrollment is paid (free courses or payment confirmed)."""
        if self.course.fee == 0:
            return True
        return self.payment_confirmed_at is not None


class LessonProgress(models.Model):
    enrollment = models.ForeignKey(Enrollment, on_delete=models.CASCADE, related_name='lesson_progress')
    lesson = models.ForeignKey(ModuleLesson, on_delete=models.CASCADE, related_name='progress_records')
    completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ('enrollment', 'lesson')

    def __str__(self):
        return f'{self.enrollment.user.email} - {self.lesson.title} ({"Done" if self.completed else "Pending"})'
