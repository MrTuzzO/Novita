from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import BabyCareRequestForm
from .models import BabyCareRequest


@login_required
def request_care(request):
    if request.method == 'POST':
        form = BabyCareRequestForm(request.POST)
        if form.is_valid():
            care_request = form.save(commit=False)
            care_request.user = request.user
            care_request.save()
            messages.success(
                request,
                f'Day care request submitted. Your request ID is {care_request.request_id}.',
            )
            return redirect('babycare:request_detail', request_id=care_request.request_id)
    else:
        initial = {
            'parent_full_name': request.user.get_full_name(),
            'email': request.user.email,
            'phone_number': request.user.phone_number,
        }
        form = BabyCareRequestForm(initial=initial)

    return render(request, 'babycare/request_care.html', {'form': form})


@login_required
def track_status(request):
    if request.user.is_staff:
        requests_qs = BabyCareRequest.objects.all().prefetch_related('updates')
    else:
        requests_qs = BabyCareRequest.objects.filter(user=request.user).prefetch_related('updates')
    return render(request, 'babycare/track_status.html', {'requests_qs': requests_qs})


@login_required
def request_detail(request, request_id):
    base_qs = BabyCareRequest.objects.prefetch_related('updates')
    if request.user.is_staff:
        care_request = get_object_or_404(base_qs, request_id=request_id)
    else:
        care_request = get_object_or_404(base_qs, request_id=request_id, user=request.user)

    updates = care_request.updates.filter(is_visible_to_parent=True)
    return render(
        request,
        'babycare/request_detail.html',
        {
            'care_request': care_request,
            'updates': updates,
        },
    )


@login_required
def my_requests(request):
    return redirect('babycare:track_status')
