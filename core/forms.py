from django import forms

from .models import ContactMessage, ExpertApplication
from service.models import ServiceType

_INPUT = (
    'w-full rounded-xl border border-slate-300 px-4 py-2.5 text-slate-800 '
    'placeholder:text-slate-400 focus:outline-none focus:ring-2 '
    'focus:ring-[var(--color-primary)] focus:border-transparent'
)


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ['full_name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 6}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', _INPUT)


class ExpertApplicationForm(forms.ModelForm):
    services = forms.ModelMultipleChoiceField(
        queryset=ServiceType.objects.filter(is_active=True),
        widget=forms.CheckboxSelectMultiple,
        required=True,
        label='Services you can provide',
        help_text='Select all services that apply.',
    )

    class Meta:
        model = ExpertApplication
        fields = ['full_name', 'email', 'phone_number', 'title', 'bio',
                  'specialization', 'years_of_experience', 'services', 'document']
        widgets = {
            'bio': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for name, field in self.fields.items():
            if name not in ('services', 'document'):
                field.widget.attrs.setdefault('class', _INPUT)

    def clean_document(self):
        doc = self.cleaned_data.get('document')
        if doc:
            allowed_ext = ['.pdf', '.doc', '.docx', '.jpg', '.jpeg', '.png']
            import os
            ext = os.path.splitext(doc.name)[1].lower()
            if ext not in allowed_ext:
                raise forms.ValidationError('Only PDF, DOC, DOCX, JPG, and PNG files are allowed.')
            if doc.size > 10 * 1024 * 1024:
                raise forms.ValidationError('File size must not exceed 10 MB.')
        return doc
