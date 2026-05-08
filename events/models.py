from django.conf import settings
from django.db import models


class Event(models.Model):
    CATEGORY_RECOVERY = 'recovery'
    CATEGORY_WELLNESS = 'wellness'
    CATEGORY_COMMUNITY = 'community'
    CATEGORY_WORKSHOP = 'workshop'

    CATEGORY_CHOICES = [
        (CATEGORY_RECOVERY, 'Recovery Program'),
        (CATEGORY_WELLNESS, 'Wellness Session'),
        (CATEGORY_COMMUNITY, 'Community Event'),
        (CATEGORY_WORKSHOP, 'Workshop'),
    ]

    title = models.CharField(max_length=160)
    summary = models.TextField()
    image = models.ImageField(upload_to='events/', blank=True, null=True)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default=CATEGORY_RECOVERY)
    event_date = models.DateField()
    location = models.CharField(max_length=140)
    is_active = models.BooleanField(default=True)
    interested_users = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name='interested_events',
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['event_date', 'title']

    def __str__(self):
        return self.title

    @property
    def interested_count(self):
        return self.interested_users.count()
