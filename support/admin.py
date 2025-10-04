from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from .models import SupportTicket, TicketResponse, TicketAttachment

class TicketAttachmentInline(admin.TabularInline):
    model = TicketAttachment
    extra = 0
    readonly_fields = ('original_filename', 'file_size_mb', 'uploaded_by', 'uploaded_at')
    
    def file_size_mb(self, obj):
        return f"{obj.file_size_mb} MB"
    file_size_mb.short_description = "Size"

class TicketResponseInline(admin.TabularInline):
    model = TicketResponse
    extra = 0
    readonly_fields = ('user', 'created_at', 'is_staff_response')
    fields = ('user', 'message', 'is_staff_response', 'created_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')

@admin.register(SupportTicket)
class SupportTicketAdmin(admin.ModelAdmin):
    list_display = (
        'ticket_id', 
        'subject_short', 
        'user_display', 
        'category', 
        'priority_badge', 
        'status_badge', 
        'response_count',
        'assigned_to',
        'created_at'
    )
    list_filter = ('status', 'priority', 'category', 'created_at', 'assigned_to')
    search_fields = ('ticket_id', 'subject', 'user__email', 'user__full_name', 'description')
    readonly_fields = ('ticket_id', 'created_at', 'updated_at', 'response_count', 'last_response_info')
    
    fieldsets = (
        ('Ticket Information', {
            'fields': ('ticket_id', 'user', 'subject', 'category', 'description')
        }),
        ('Status & Priority', {
            'fields': ('status', 'priority', 'assigned_to')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'closed_at'),
            'classes': ('collapse',)
        }),
        ('Statistics', {
            'fields': ('response_count', 'last_response_info'),
            'classes': ('collapse',)
        })
    )
    
    inlines = [TicketResponseInline, TicketAttachmentInline]
    
    def subject_short(self, obj):
        return obj.subject[:50] + '...' if len(obj.subject) > 50 else obj.subject
    subject_short.short_description = 'Subject'
    
    def user_display(self, obj):
        name = obj.user.get_full_name()
        return format_html(
            '<span title="{}">{}</span>',
            obj.user.email,
            name[:20] + '...' if len(name) > 20 else name
        )
    user_display.short_description = 'User'
    
    def priority_badge(self, obj):
        colors = {
            'low': 'success',
            'medium': 'warning',
            'high': 'danger',
            'critical': 'dark'
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.priority, 'secondary'),
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def status_badge(self, obj):
        colors = {
            'open': 'primary',
            'in_progress': 'info',
            'waiting_for_customer': 'warning',
            'resolved': 'success',
            'closed': 'secondary'
        }
        return format_html(
            '<span class="badge bg-{}">{}</span>',
            colors.get(obj.status, 'secondary'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def last_response_info(self, obj):
        last_response = obj.last_response
        if last_response:
            return format_html(
                '{} - {} ago',
                last_response.user.get_full_name(),
                last_response.created_at
            )
        return "No responses yet"
    last_response_info.short_description = 'Last Response'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'assigned_to').prefetch_related('responses')

@admin.register(TicketResponse)
class TicketResponseAdmin(admin.ModelAdmin):
    list_display = ('ticket_link', 'user_display', 'message_preview', 'is_staff_response', 'created_at')
    list_filter = ('is_staff_response', 'created_at')
    search_fields = ('ticket__ticket_id', 'ticket__subject', 'user__email', 'message')
    readonly_fields = ('is_staff_response', 'created_at')
    
    def ticket_link(self, obj):
        url = reverse('admin:support_supportticket_change', args=[obj.ticket.id])
        return format_html('<a href="{}">{}</a>', url, obj.ticket.ticket_id)
    ticket_link.short_description = 'Ticket'
    
    def user_display(self, obj):
        return obj.user.get_full_name()
    user_display.short_description = 'User'
    
    def message_preview(self, obj):
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message'

@admin.register(TicketAttachment)
class TicketAttachmentAdmin(admin.ModelAdmin):
    list_display = ('ticket_link', 'original_filename', 'file_size_display', 'uploaded_by', 'uploaded_at')
    list_filter = ('uploaded_at',)
    search_fields = ('ticket__ticket_id', 'original_filename', 'uploaded_by__email')
    readonly_fields = ('original_filename', 'file_size', 'uploaded_at')
    
    def ticket_link(self, obj):
        url = reverse('admin:support_supportticket_change', args=[obj.ticket.id])
        return format_html('<a href="{}">{}</a>', url, obj.ticket.ticket_id)
    ticket_link.short_description = 'Ticket'
    
    def file_size_display(self, obj):
        return f"{obj.file_size_mb} MB"
    file_size_display.short_description = 'Size'
