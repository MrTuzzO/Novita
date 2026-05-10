from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .forms import AdmissionRequestForm
from .models import AdmissionRequest


@login_required
def request_admission(request):
    if request.method == 'POST':
        form = AdmissionRequestForm(request.POST)
        if form.is_valid():
            admission = form.save(commit=False)
            admission.user = request.user
            admission.save()
            messages.success(
                request,
                f'Admission request submitted. Your application ID is {admission.application_id}.',
            )
            return redirect('rehab:application_detail', application_id=admission.application_id)
    else:
        initial = {
            'full_name': request.user.get_full_name(),
            'email': request.user.email,
            'phone_number': request.user.phone_number,
        }
        form = AdmissionRequestForm(initial=initial)

    return render(request, 'rehab/request_admission.html', {'form': form})


def book_counseling_redirect(request):
    return redirect('service:create_inquiry')


@login_required
def track_status(request):
    if request.user.is_staff:
        applications = AdmissionRequest.objects.all().prefetch_related('updates')
    else:
        applications = AdmissionRequest.objects.filter(user=request.user).prefetch_related('updates')
    return render(request, 'rehab/track_status.html', {'applications': applications})


@login_required
def application_detail(request, application_id):
    base_qs = AdmissionRequest.objects.prefetch_related('updates')
    if request.user.is_staff:
        application = get_object_or_404(base_qs, application_id=application_id)
    else:
        application = get_object_or_404(base_qs, application_id=application_id, user=request.user)

    updates = application.updates.filter(is_visible_to_applicant=True)
    return render(
        request,
        'rehab/application_detail.html',
        {
            'application': application,
            'updates': updates,
        },
    )


@login_required
def my_applications(request):
    return redirect('rehab:track_status')
