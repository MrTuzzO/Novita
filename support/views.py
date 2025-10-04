from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from django.http import HttpResponse, Http404
from django.core.files.storage import default_storage
from django.conf import settings
import os

from .models import SupportTicket, TicketResponse, TicketAttachment
from .forms import SupportTicketForm, TicketResponseForm, TicketSearchForm

@login_required
def ticket_list(request):
    """List user's support tickets"""
    tickets = SupportTicket.objects.filter(user=request.user).select_related('assigned_to')
    
    # Search and filter
    search_form = TicketSearchForm(request.GET)
    if search_form.is_valid():
        search_query = search_form.cleaned_data.get('search')
        status_filter = search_form.cleaned_data.get('status')
        category_filter = search_form.cleaned_data.get('category')
        priority_filter = search_form.cleaned_data.get('priority')
        
        if search_query:
            tickets = tickets.filter(
                Q(ticket_id__icontains=search_query) |
                Q(subject__icontains=search_query) |
                Q(description__icontains=search_query)
            )
        
        if status_filter:
            tickets = tickets.filter(status=status_filter)
        
        if category_filter:
            tickets = tickets.filter(category=category_filter)
            
        if priority_filter:
            tickets = tickets.filter(priority=priority_filter)
    
    # Pagination
    paginator = Paginator(tickets, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'search_form': search_form,
        'total_tickets': tickets.count(),
    }
    return render(request, 'support/ticket_list.html', context)

@login_required
def create_ticket(request):
    """Create new support ticket"""
    if request.method == 'POST':
        form = SupportTicketForm(request.POST, request.FILES, user=request.user)
        if form.is_valid():
            ticket = form.save()
            
            # Handle file attachments
            files = request.FILES.getlist('attachments')
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf']
            
            for file in files:
                # Check file extension
                file_ext = file.name.lower().split('.')[-1]
                if f'.{file_ext}' not in allowed_extensions:
                    messages.warning(request, f'File {file.name} is not supported. Only JPG, PNG, GIF, and PDF files are allowed.')
                    continue
                    
                # Check file size
                if file.size <= 10 * 1024 * 1024:  # 10MB limit
                    TicketAttachment.objects.create(
                        ticket=ticket,
                        file=file,
                        uploaded_by=request.user,
                        original_filename=file.name,
                        file_size=file.size
                    )
                else:
                    messages.warning(request, f'File {file.name} is too large (max 10MB)')
            
            messages.success(request, f'Support ticket #{ticket.ticket_id} has been created successfully!')
            return redirect('support:ticket_detail', ticket_id=ticket.ticket_id)
    else:
        form = SupportTicketForm(user=request.user)
    
    context = {
        'form': form,
        'title': 'Create Support Ticket'
    }
    return render(request, 'support/create_ticket.html', context)

@login_required
def ticket_detail(request, ticket_id):
    """View ticket details and responses"""
    ticket = get_object_or_404(
        SupportTicket.objects.select_related('user', 'assigned_to'),
        ticket_id=ticket_id
    )
    
    # Check if user can view this ticket
    if not (ticket.user == request.user or request.user.is_staff):
        raise Http404("Ticket not found")
    
    # Get responses and attachments
    responses = ticket.responses.select_related('user').prefetch_related('attachments')
    attachments = ticket.attachments.filter(response__isnull=True)  # Ticket-level attachments
    
    # Forms
    response_form = TicketResponseForm(user=request.user, ticket=ticket)
    
    # Handle POST requests
    if request.method == 'POST':
        if 'submit_response' in request.POST:
            response_form = TicketResponseForm(
                request.POST, 
                request.FILES, 
                user=request.user, 
                ticket=ticket
            )
            if response_form.is_valid():
                response = response_form.save()
                
                # Handle response attachments
                files = request.FILES.getlist('attachments')
                allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif', '.pdf']
                
                for file in files:
                    # Check file extension
                    file_ext = file.name.lower().split('.')[-1]
                    if f'.{file_ext}' not in allowed_extensions:
                        messages.warning(request, f'File {file.name} is not supported. Only JPG, PNG, GIF, and PDF files are allowed.')
                        continue
                        
                    # Check file size
                    if file.size <= 10 * 1024 * 1024:  # 10MB limit
                        TicketAttachment.objects.create(
                            ticket=ticket,
                            response=response,
                            file=file,
                            uploaded_by=request.user,
                            original_filename=file.name,
                            file_size=file.size
                        )
                    else:
                        messages.warning(request, f'File {file.name} is too large (max 10MB)')
                
                # Update ticket status if customer responds
                if not request.user.is_staff and ticket.status == 'waiting_for_customer':
                    ticket.status = 'open'
                    ticket.save()
                
                messages.success(request, 'Your response has been added successfully!')
                return redirect('support:ticket_detail', ticket_id=ticket.ticket_id)
        
        # Admin form handling removed - use Django admin for ticket management
    
    context = {
        'ticket': ticket,
        'responses': responses,
        'attachments': attachments,
        'response_form': response_form,
    }
    return render(request, 'support/ticket_detail.html', context)

@login_required
def close_ticket(request, ticket_id):
    """Close a support ticket"""
    if request.method != 'POST':
        return redirect('support:ticket_detail', ticket_id=ticket_id)
        
    ticket = get_object_or_404(SupportTicket, ticket_id=ticket_id)
    
    # Check permissions
    if not (ticket.user == request.user or request.user.is_staff):
        raise Http404("Ticket not found")
    
    ticket.status = 'closed'
    ticket.save()
    
    messages.success(request, f'Ticket #{ticket.ticket_id} has been closed.')
    return redirect('support:ticket_detail', ticket_id=ticket.ticket_id)

@login_required
def download_attachment(request, attachment_id):
    """Download ticket attachment"""
    attachment = get_object_or_404(TicketAttachment, id=attachment_id)
    
    # Check permissions
    if not (attachment.ticket.user == request.user or request.user.is_staff):
        raise Http404("File not found")
    
    try:
        response = HttpResponse(attachment.file.read(), content_type='application/octet-stream')
        response['Content-Disposition'] = f'attachment; filename="{attachment.original_filename}"'
        return response
    except FileNotFoundError:
        messages.error(request, 'File not found on server.')
        return redirect('support:ticket_detail', ticket_id=attachment.ticket.ticket_id)

