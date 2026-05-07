from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from .models import Event


def event_list(request):
    events = Event.objects.filter(is_active=True).order_by('event_date')
    return render(request, 'events/list.html', {'events': events})


def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    related_events = Event.objects.filter(is_active=True).exclude(pk=event.pk).order_by('event_date')[:3]
    return render(request, 'events/detail.html', {
        'event': event,
        'related_events': related_events,
    })


@login_required
@require_POST
def toggle_interest(request, pk):
    event = get_object_or_404(Event, pk=pk, is_active=True)
    if event.interested_users.filter(pk=request.user.pk).exists():
        event.interested_users.remove(request.user)
    else:
        event.interested_users.add(request.user)

    return redirect(request.POST.get('next') or 'home')
