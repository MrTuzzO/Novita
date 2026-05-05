from django import forms
from django.contrib.auth import get_user_model

from .models import ServiceInquiry, ServiceMessage

User = get_user_model()

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


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class MultipleFileField(forms.FileField):
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('widget', MultipleFileInput())
        super().__init__(*args, **kwargs)

    def clean(self, data, initial=None):
        single_file_clean = super().clean
        if isinstance(data, (list, tuple)):
            result = []
            for item in data:
                if item:
                    cleaned = single_file_clean(item, initial)
                    if cleaned:
                        result.append(cleaned)
            return result

        cleaned = single_file_clean(data, initial)
        return [cleaned] if cleaned else []


class ServiceInquiryForm(forms.ModelForm):
    message = forms.CharField(widget=forms.Textarea(attrs={'rows': 6}), label='Your Message')
    attachments = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={
            'class': _FILE,
            'accept': '.jpg,.jpeg,.png,.gif,.pdf,.txt,.doc,.docx'
        }),
        help_text='Optional: JPG, PNG, GIF, PDF, TXT, DOC, DOCX (max 10MB each)'
    )

    class Meta:
        model = ServiceInquiry
        fields = ['service_type', 'expert', 'subject']

    def __init__(self, *args, **kwargs):
        selected_service = kwargs.pop('selected_service', None)
        super().__init__(*args, **kwargs)

        for field in ['service_type', 'expert', 'subject', 'message']:
            self.fields[field].widget.attrs.setdefault('class', _INPUT)

        self.fields['service_type'].queryset = self.fields['service_type'].queryset.filter(is_active=True)
        expert_queryset = User.objects.filter(role='expert', is_active=True, expert_profile__is_available=True).select_related('expert_profile')
        if selected_service:
            expert_queryset = expert_queryset.filter(expert_profile__services=selected_service)
        self.fields['expert'].queryset = expert_queryset.distinct()
        self.fields['expert'].required = False

    def clean(self):
        cleaned_data = super().clean()
        service_type = cleaned_data.get('service_type')
        expert = cleaned_data.get('expert')

        if expert and expert.role != 'expert':
            self.add_error('expert', 'Selected user is not an expert.')

        if service_type and expert and (not hasattr(expert, 'expert_profile') or not expert.expert_profile.services.filter(id=service_type.id).exists()):
            self.add_error('expert', 'Selected expert does not serve this category.')

        return cleaned_data


class ServiceMessageForm(forms.ModelForm):
    attachments = MultipleFileField(
        required=False,
        widget=MultipleFileInput(attrs={
            'class': _FILE,
            'accept': '.jpg,.jpeg,.png,.gif,.pdf,.txt,.doc,.docx'
        }),
    )

    class Meta:
        model = ServiceMessage
        fields = ['message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 4, 'class': _INPUT, 'placeholder': 'Type your message...'}),
        }


class ServiceInquiryStatusForm(forms.ModelForm):
    class Meta:
        model = ServiceInquiry
        fields = ['status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].widget.attrs.setdefault('class', _INPUT)
