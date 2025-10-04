from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone

User = get_user_model()

class SupportTicket(models.Model):
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('open', 'Open'),
        ('in_progress', 'In Progress'),
        ('waiting_for_customer', 'Waiting for Customer'),
        ('resolved', 'Resolved'),
        ('closed', 'Closed'),
    ]
    
    CATEGORY_CHOICES = [
        ('recovery_support', 'Recovery & Addiction Support'),
        ('mental_health', 'Mental Health Assistance'),
        ('cyber_safety', 'Cyber Safety & Online Harassment'),
        ('emergency_crisis', 'Emergency/Crisis Intervention'),
        ('account_privacy', 'Account & Privacy Issues'),
        ('technical', 'Technical Problems'),
        ('resources', 'Resources & Information Request'),
        ('community', 'Community & Group Support'),
        ('other', 'Other'),
    ]
    
    # Basic ticket info
    ticket_id = models.CharField(max_length=20, unique=True, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='support_tickets')
    subject = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    priority = models.CharField(max_length=10, choices=PRIORITY_CHOICES, default='medium')
    status = models.CharField(max_length=25, choices=STATUS_CHOICES, default='open')
    
    # Description
    description = models.TextField(help_text="Please describe your issue in detail")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    closed_at = models.DateTimeField(null=True, blank=True)
    
    # Admin assignment
    assigned_to = models.ForeignKey(
        User, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='assigned_tickets',
        limit_choices_to={'is_staff': True}
    )
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = "Support Ticket"
        verbose_name_plural = "Support Tickets"
    
    def __str__(self):
        return f"#{self.ticket_id} - {self.subject}"
    
    def save(self, *args, **kwargs):
        if not self.ticket_id:
            # Generate unique ticket ID
            import random
            import string
            while True:
                ticket_id = 'TK' + ''.join(random.choices(string.digits, k=8))
                if not SupportTicket.objects.filter(ticket_id=ticket_id).exists():
                    self.ticket_id = ticket_id
                    break
        
        # Set closed_at when status changes to closed
        if self.status == 'closed' and not self.closed_at:
            self.closed_at = timezone.now()
        elif self.status != 'closed':
            self.closed_at = None
            
        super().save(*args, **kwargs)
    
    def get_absolute_url(self):
        return reverse('support:ticket_detail', kwargs={'ticket_id': self.ticket_id})
    
    @property
    def is_open(self):
        return self.status in ['open', 'in_progress', 'waiting_for_customer']
    
    @property
    def response_count(self):
        return self.responses.count()
    
    @property
    def last_response(self):
        return self.responses.order_by('-created_at').first()

class TicketResponse(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='responses')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_staff_response = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"Response to {self.ticket.ticket_id} by {self.user.get_full_name()}"
    
    def save(self, *args, **kwargs):
        # Automatically set is_staff_response based on user
        self.is_staff_response = self.user.is_staff
        super().save(*args, **kwargs)

class TicketAttachment(models.Model):
    ticket = models.ForeignKey(SupportTicket, on_delete=models.CASCADE, related_name='attachments')
    response = models.ForeignKey(TicketResponse, on_delete=models.CASCADE, null=True, blank=True, related_name='attachments')
    file = models.FileField(upload_to='support/attachments/%Y/%m/')
    original_filename = models.CharField(max_length=255)
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    file_size = models.PositiveIntegerField(help_text="File size in bytes")
    
    class Meta:
        ordering = ['-uploaded_at']
    
    def __str__(self):
        return f"Attachment: {self.original_filename}"
    
    def save(self, *args, **kwargs):
        if self.file:
            self.original_filename = self.file.name
            self.file_size = self.file.size
        super().save(*args, **kwargs)
    
    @property
    def file_size_mb(self):
        return round(self.file_size / (1024 * 1024), 2)
