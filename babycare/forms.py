from django import forms

from .models import BabyCareRequest

_INPUT = (
    'w-full rounded-xl border border-slate-300 px-4 py-2.5 text-slate-800 '
    'placeholder:text-slate-400 focus:outline-none focus:ring-2 '
    'focus:ring-[var(--color-primary)] focus:border-transparent'
)


class BabyCareRequestForm(forms.ModelForm):
    class Meta:
        model = BabyCareRequest
        fields = [
            'parent_full_name',
            'email',
            'phone_number',
            'child_name',
            'child_age_years',
            'care_shift',
            'preferred_start_date',
            'care_requirements',
        ]
        widgets = {
            'preferred_start_date': forms.DateInput(attrs={'type': 'date'}),
            'care_requirements': forms.Textarea(attrs={'rows': 5}),
        }
        labels = {
            'parent_full_name': 'Parent/Guardian Full Name',
            'phone_number': 'Phone Number',
            'child_name': 'Child Full Name',
            'child_age_years': 'Child Age (Years)',
            'care_shift': 'Preferred Day Care Shift',
            'preferred_start_date': 'Preferred Start Date',
            'care_requirements': 'Child Care Requirements',
        }
        help_texts = {
            'care_requirements': 'Include meal instructions, allergy notes, nap routine, medication notes, or any special support details.',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.setdefault('class', _INPUT)
