from django import forms

from .models import AdmissionRequest

_INPUT = (
    'w-full rounded-xl border border-slate-300 px-4 py-2.5 text-slate-800 '
    'placeholder:text-slate-400 focus:outline-none focus:ring-2 '
    'focus:ring-[var(--color-primary)] focus:border-transparent'
)


class AdmissionRequestForm(forms.ModelForm):
    class Meta:
        model = AdmissionRequest
        fields = [
            'full_name',
            'email',
            'phone_number',
            'age',
            'preferred_admission_date',
            'primary_concern',
        ]
        widgets = {
            'preferred_admission_date': forms.DateInput(attrs={'type': 'date'}),
            'primary_concern': forms.Textarea(attrs={'rows': 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', _INPUT)
