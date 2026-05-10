from django.conf import settings
from django.db import models


class Donation(models.Model):
    donor_name = models.CharField(max_length=120)
    donor_email = models.EmailField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    message = models.TextField(blank=True)
    stripe_session_id = models.CharField(max_length=200, blank=True)
    is_confirmed = models.BooleanField(default=False)
    donated_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-donated_at']

    def __str__(self):
        return f'{self.donor_name} – ৳{self.amount}'


class Banner(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    image = models.ImageField(upload_to='banners/')
    link = models.URLField(blank=True, null=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.title


class ContactMessage(models.Model):
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    subject = models.CharField(max_length=180)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'{self.full_name} - {self.subject}'


class ExpertApplication(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone_number = models.CharField(max_length=20, blank=True)
    title = models.CharField(max_length=120)
    bio = models.TextField()
    specialization = models.CharField(max_length=200, blank=True)
    years_of_experience = models.PositiveIntegerField(default=0)
    services = models.ManyToManyField('service.ServiceType', related_name='expert_applications')
    document = models.FileField(
        upload_to='expert_applications/documents/%Y/%m/',
        blank=True,
        null=True,
        help_text='Upload your CV, certifications, or any supporting credential documents (PDF, DOC, DOCX, JPG, PNG — max 10 MB).',
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-submitted_at']
        verbose_name = 'Expert Application'
        verbose_name_plural = 'Expert Applications'

    def __str__(self):
        return f'{self.full_name} – {self.title}'