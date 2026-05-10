from django import template
from django.db.models import Count, Sum

register = template.Library()


@register.simple_tag
def donation_stats():
    from core.models import Donation
    return Donation.objects.filter(is_confirmed=True).aggregate(
        total_amount=Sum('amount'),
        total_count=Count('id'),
    )
