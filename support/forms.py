from django import forms
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML, Div, Field
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

class SupportTicketForm(forms.ModelForm):
    attachments = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={
            'class': 'form-control',
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
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'subject',
            Row(
                Column('category', css_class='form-group col-md-6 mb-3'),
                Column('priority', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'description',
            'attachments',
            HTML('<small class="text-muted">Supported file types: JPG, PNG, GIF, PDF (Max 10MB each)</small>'),
            Div(
                Submit('submit', 'Create Support Ticket', css_class='btn btn-primary'),
                css_class='d-flex justify-content-center mt-4'
            )
        )
        
        # Customize field attributes
        for field_name, field in self.fields.items():
            if field_name != 'attachments':
                field.widget.attrs.update({'class': 'form-control'})
        
        # Customize labels and help text
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
            'class': 'form-control',
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
                'class': 'form-control'
            })
        }
    
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.ticket = kwargs.pop('ticket', None)
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'message',
            'attachments',
            Div(
                Submit('submit_response', 'Send Response', css_class='btn btn-primary'),
                css_class='d-flex justify-content-end mt-3'
            )
        )
        
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
        
        # Limit assigned_to to staff members only
        self.fields['assigned_to'].queryset = User.objects.filter(is_staff=True)
        self.fields['assigned_to'].empty_label = "Unassigned"
        
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Row(
                Column('status', css_class='form-group col-md-4 mb-3'),
                Column('priority', css_class='form-group col-md-4 mb-3'),
                Column('assigned_to', css_class='form-group col-md-4 mb-3'),
                css_class='form-row'
            ),
            Div(
                Submit('update_ticket', 'Update Ticket', css_class='btn btn-warning'),
                css_class='d-flex justify-content-end'
            )
        )
        
        # Add CSS classes
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

class TicketSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Search tickets...',
            'class': 'form-control'
        })
    )
    status = forms.ChoiceField(
        choices=[('', 'All Status')] + SupportTicket.STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    category = forms.ChoiceField(
        choices=[('', 'All Categories')] + SupportTicket.CATEGORY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    priority = forms.ChoiceField(
        choices=[('', 'All Priorities')] + SupportTicket.PRIORITY_CHOICES,
        required=False,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.form_method = 'GET'
        self.helper.layout = Layout(
            Row(
                Column('search', css_class='form-group col-md-4 mb-3'),
                Column('status', css_class='form-group col-md-3 mb-3'),
                Column('category', css_class='form-group col-md-3 mb-3'),
                Column('priority', css_class='form-group col-md-2 mb-3'),
                css_class='form-row'
            ),
            Div(
                Submit('filter', 'Filter', css_class='btn btn-primary'),
                HTML('<a href="?" class="btn btn-outline-secondary ms-2">Clear</a>'),
                css_class='d-flex justify-content-center'
            )
        )