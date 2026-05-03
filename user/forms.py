from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import get_user_model

User = get_user_model()

_INPUT = (
    'w-full rounded-xl border border-slate-300 px-4 py-2.5 text-slate-800 '
    'placeholder:text-slate-400 focus:outline-none focus:ring-2 '
    'focus:ring-[var(--color-primary)] focus:border-transparent'
)


class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=100, required=False, label='Full Name')

    class Meta:
        model = User
        fields = ('email', 'full_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault('class', _INPUT)

        self.fields['email'].widget.attrs.update({'placeholder': 'your@email.com', 'type': 'email'})
        self.fields['full_name'].widget.attrs.update({'placeholder': 'Your full name'})

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.full_name = self.cleaned_data['full_name']
        if commit:
            user.save()
        return user


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = ('email', 'full_name')


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['full_name', 'date_of_birth', 'address', 'school_college_name', 'phone_number']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.setdefault('class', _INPUT)

        self.fields['full_name'].label = 'Full Name'
        self.fields['date_of_birth'].label = 'Date of Birth'
        self.fields['address'].label = 'Address'
        self.fields['school_college_name'].label = 'School/College Name'
        self.fields['phone_number'].label = 'Phone Number'


class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.fields['username'].label = 'Email'
        self.fields['username'].widget.attrs.update({
            'class': _INPUT,
            'placeholder': 'your@email.com',
            'type': 'email',
        })
        self.fields['password'].widget.attrs.update({
            'class': _INPUT,
            'placeholder': 'Enter your password',
        })