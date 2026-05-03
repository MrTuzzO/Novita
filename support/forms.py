from django import forms
from django.contrib.auth import get_user_model
from .models import SupportTicket, TicketResponse, TicketAttachment

User = get_user_model()

class MultipleFileInput(forms.ClearableFileInput):
    """Custom widget for multiple file uploads"""
    allow_multiple_selected = True

class MultipleFileField(forms.FileField):
    """Custom field for multiple file uploads"""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault("widget", MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = []
            for d in data:
                if d:  # Only process non-empty files
                    cleaned_file = single_file_clean(d, initial)
                    if cleaned_file:
                        result.append(cleaned_file)
            return result
        else:
            result = single_file_clean(data, initial)
            return [result] if result else []

_INPUT = (
    'w-full rounded-xl border border-slate-300 px-4 py-2.5 text-slate-800 '
    'placeholder:text-slate-400 focus:outline-none focus:ring-2 '
    'focus:ring-[var(--color-primary)] focus:border-transparent'
)
_FILE = (
    'w-full rounded-xl border border-slate-300 px-4 py-2 text-sm text-slate-800 '
    'file:mr-4 file:rounded-lg file:border-0 file:bg-[var(--color-primary)]/10 '
    'file:px-4 file:py-2 file:text-sm file:font-semibold file:text-[var(--color-primary)]'
)


class SupportTicketForm(forms.ModelForm):
    attachments = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={
            'class': _FILE,
            'accept': '.jpg,.jpeg,.png,.gif,.pdf'
        }),
        help_text="Upload images (JPG, PNG, GIF) or PDF files (max 10MB each)"
    )
    
    class Meta:
        model = SupportTicket
        fields = ['subject', 'category', 'priority', 'description']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 6}),
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        for field_name, field in self.fields.items():
            if field_name != 'attachments':
                field.widget.attrs.setdefault('class', _INPUT)

        self.fields['subject'].label = 'How can Novita support you today?'
        self.fields['subject'].help_text = 'Brief title describing your support need or concern'
        self.fields['category'].label = 'Support Type'
        self.fields['category'].help_text = 'Choose the area where you need assistance - recovery, mental health, cyber safety, or emergency support'
        self.fields['priority'].label = 'Urgency Level'
        self.fields['priority'].help_text = 'Critical = Immediate danger/crisis | High = Urgent but not life-threatening | Medium = Important | Low = General inquiry'
        self.fields['description'].label = 'Tell us what\'s happening'
        self.fields['description'].help_text = 'Share as much detail as you\'re comfortable with. For emergencies, also call local authorities or crisis hotlines immediately.'
    
    def save(self, commit=True):
        ticket = super().save(commit=False)
        if self.user:
            ticket.user = self.user
        if commit:
            ticket.save()
        return ticket

class TicketResponseForm(forms.ModelForm):
    attachments = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={
            'class': _FILE,
            'accept': '.jpg,.jpeg,.png,.gif,.pdf'
        }),
        help_text="Attach images or PDF files to your response (optional)"
    )
    
    class Meta:
        model = TicketResponse
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 4,
                'placeholder': 'Type your response here...',
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.ticket = kwargs.pop('ticket', None)
        super().__init__(*args, **kwargs)

        self.fields['message'].widget.attrs.setdefault('class', _INPUT)
        self.fields['message'].label = 'Your Response'
    
    def save(self, commit=True):
        response = super().save(commit=False)
        if self.user:
            response.user = self.user
        if self.ticket:
            response.ticket = self.ticket
        if commit:
            response.save()
        return response

class AdminTicketUpdateForm(forms.ModelForm):
    """Form for admin to update ticket status and assignment"""
    
    class Meta:
        model = SupportTicket
        fields = ['status', 'priority', 'assigned_to']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['assigned_to'].queryset = User.objects.filter(is_staff=True)
        self.fields['assigned_to'].empty_label = "Unassigned"
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', _INPUT)

class TicketSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search tickets...',
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + SupportTicket.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={})
    )
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + SupportTicket.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={})
    )
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + SupportTicket.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)