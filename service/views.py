from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import Http404, HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import ListView

from .forms import ServiceInquiryForm, ServiceInquiryStatusForm, ServiceMessageForm
from .models import ExpertProfile, ServiceInquiry, ServiceMessage, ServiceMessageAttachment, ServiceType

User = get_user_model()


SERVICE_TEMPLATE_MAP = {
    'cyber-security': 'service/cyber_security.html',
    'lawyer': 'service/lawyer.html',
    'doctor': 'service/doctor.html',
    'detective': 'service/detective.html',
}


class ServiceListView(ListView):
    template_name = 'service/list.html'
    context_object_name = 'services'

    def get_queryset(self):
        return ServiceType.objects.filter(is_active=True).order_by('name')


def service_detail(request, slug):
    service = get_object_or_404(ServiceType, slug=slug, is_active=True)
    experts = ExpertProfile.objects.filter(
        is_available=True,
        user__is_active=True,
        user__role='expert',
        services=service,
    ).select_related('user').distinct()

    template_name = SERVICE_TEMPLATE_MAP.get(slug, 'service/detail.html')
    context = {
        'service': service,
        'experts': experts,
    }
    return render(request, template_name, context)


@login_required
def create_inquiry(request):
    service_slug = request.GET.get('service')
    service_id = request.POST.get('service_type')
    expert_id = request.GET.get('expert') or request.POST.get('expert')
    selected_service = None
    if service_slug:
        selected_service = ServiceType.objects.filter(slug=service_slug, is_active=True).first()
    elif service_id:
        selected_service = ServiceType.objects.filter(id=service_id, is_active=True).first()
    selected_expert = User.objects.filter(id=expert_id, role='expert', is_active=True).first() if expert_id else None

    if request.method == 'POST':
        form = ServiceInquiryForm(request.POST, request.FILES, selected_service=selected_service)
        if form.is_valid():
            inquiry = form.save(commit=False)
            inquiry.user = request.user
            inquiry.save()

            first_message = ServiceMessage.objects.create(
                inquiry=inquiry,
                user=request.user,
                message=form.cleaned_data['message'],
            )
            _save_attachments(request, form.cleaned_data.get('attachments', []), first_message)

            messages.success(request, f'Your service request {inquiry.inquiry_id} has been sent.')
            return redirect('service:inquiry_detail', inquiry_id=inquiry.inquiry_id)
    else:
        initial = {}
        if selected_service:
            initial['service_type'] = selected_service
        if selected_expert:
            initial['expert'] = selected_expert
        form = ServiceInquiryForm(initial=initial, selected_service=selected_service)

    return render(request, 'service/contact_form.html', {'form': form})


@login_required
def inquiry_list(request):
    inquiries = ServiceInquiry.objects.filter(user=request.user).select_related('service_type', 'expert', 'user')

    paginator = Paginator(inquiries, 10)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(
        request,
        'service/requests/list.html',
        {
            'page_obj': page_obj,
            'total': inquiries.count(),
            'page_title': 'My Service Requests',
            'page_subtitle': 'Track your expert conversations and file-sharing threads.',
            'is_expert_view': False,
        },
    )


@login_required
def expert_inbox(request):
    if not _is_expert_user(request.user):
        raise Http404('Inbox not found')

    inquiries = ServiceInquiry.objects.filter(expert=request.user).select_related('service_type', 'expert', 'user')

    status = request.GET.get('status')
    if status:
        inquiries = inquiries.filter(status=status)

    paginator = Paginator(inquiries, 12)
    page_obj = paginator.get_page(request.GET.get('page'))
    return render(
        request,
        'service/requests/list.html',
        {
            'page_obj': page_obj,
            'total': inquiries.count(),
            'page_title': 'Expert Inbox',
            'page_subtitle': 'Manage your assigned requests and reply in async chat-style threads.',
            'is_expert_view': True,
            'current_status': status or '',
            'status_choices': ServiceInquiry.STATUS_CHOICES,
        },
    )


@login_required
def inquiry_detail(request, inquiry_id):
    inquiry = get_object_or_404(
        ServiceInquiry.objects.select_related('service_type', 'expert', 'user'),
        inquiry_id=inquiry_id,
    )
    if not (request.user == inquiry.user or request.user == inquiry.expert or request.user.is_staff):
        raise Http404('Request not found')

    form = ServiceMessageForm()
    status_form = ServiceInquiryStatusForm(instance=inquiry)

    if request.method == 'POST' and inquiry.status != ServiceInquiry.STATUS_CLOSED:
        action = request.POST.get('action', 'reply')

        if action == 'update_status' and _can_manage_status(request.user, inquiry):
            status_form = ServiceInquiryStatusForm(request.POST, instance=inquiry)
            if status_form.is_valid():
                status_form.save()
                messages.success(request, 'Request status updated.')
                return redirect('service:inquiry_detail', inquiry_id=inquiry.inquiry_id)
        else:
            form = ServiceMessageForm(request.POST, request.FILES)
            if form.is_valid():
                msg = form.save(commit=False)
                msg.inquiry = inquiry
                msg.user = request.user
                msg.save()
                _save_attachments(request, form.cleaned_data.get('attachments', []), msg)

                if request.user == inquiry.user and inquiry.status == ServiceInquiry.STATUS_WAITING_FOR_USER:
                    inquiry.status = ServiceInquiry.STATUS_OPEN
                    inquiry.save(update_fields=['status', 'updated_at'])

                if request.user == inquiry.expert and inquiry.status == ServiceInquiry.STATUS_OPEN:
                    inquiry.status = ServiceInquiry.STATUS_IN_PROGRESS
                    inquiry.save(update_fields=['status', 'updated_at'])

                messages.success(request, 'Message sent successfully.')
                return redirect('service:inquiry_detail', inquiry_id=inquiry.inquiry_id)

    all_messages_qs = inquiry.messages.select_related('user').prefetch_related('attachments')
    total_msg_count = all_messages_qs.count()
    MSG_PAGE_SIZE = 15
    show_all = request.GET.get('msg_all') == '1'
    if show_all or total_msg_count <= MSG_PAGE_SIZE:
        messages_qs = list(all_messages_qs)
        has_older = False
        older_count = 0
    else:
        messages_qs = list(all_messages_qs[total_msg_count - MSG_PAGE_SIZE:])
        has_older = True
        older_count = total_msg_count - MSG_PAGE_SIZE

    return render(
        request,
        'service/requests/detail.html',
        {
            'inquiry': inquiry,
            'messages_qs': messages_qs,
            'has_older': has_older,
            'older_count': older_count,
            'form': form,
            'status_form': status_form,
            'can_manage_status': _can_manage_status(request.user, inquiry),
        },
    )


@login_required
def close_inquiry(request, inquiry_id):
    if request.method != 'POST':
        return redirect('service:inquiry_detail', inquiry_id=inquiry_id)

    inquiry = get_object_or_404(ServiceInquiry, inquiry_id=inquiry_id)
    if not (request.user == inquiry.user or request.user.is_staff):
        raise Http404('Request not found')
    inquiry.status = ServiceInquiry.STATUS_CLOSED
    inquiry.save()
    messages.success(request, f'Request {inquiry.inquiry_id} has been closed.')
    return redirect('service:inquiry_detail', inquiry_id=inquiry.inquiry_id)


@login_required
def download_attachment(request, attachment_id):
    attachment = get_object_or_404(ServiceMessageAttachment.objects.select_related('message__inquiry'), id=attachment_id)
    inquiry = attachment.message.inquiry
    if not (request.user == inquiry.user or request.user == inquiry.expert or request.user.is_staff):
        raise Http404('File not found')
    response = HttpResponse(attachment.file.read(), content_type='application/octet-stream')
    response['Content-Disposition'] = f'attachment; filename="{attachment.original_filename}"'
    return response


def _save_attachments(request, files, message):
    allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf', '.txt', '.doc', '.docx']
    for file in files:
        file_ext = f".{file.name.lower().split('.')[-1]}"
        if file_ext not in allowed_extensions:
            messages.warning(request, f'File {file.name} is not supported and was skipped.')
            continue
        if file.size > 10 * 1024 * 1024:
            messages.warning(request, f'File {file.name} is larger than 10MB and was skipped.')
            continue
        ServiceMessageAttachment.objects.create(
            message=message,
            file=file,
            uploaded_by=request.user,
            original_filename=file.name,
            file_size=file.size,
        )


def _is_expert_user(user):
    return user.is_staff or getattr(user, 'role', None) == 'expert'


def _can_manage_status(user, inquiry):
    return user.is_staff or user == inquiry.expert


def expert_profile(request, pk):
    expert = get_object_or_404(
        ExpertProfile.objects.select_related('user').prefetch_related('services'),
        pk=pk,
        is_available=True,
        user__is_active=True,
    )
    return render(request, 'service/expert_profile.html', {'expert': expert})
