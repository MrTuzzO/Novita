from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, AuthenticationForm
from django.contrib.auth import get_user_model
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Submit, Row, Column, HTML, Div

User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    full_name = forms.CharField(max_length=100, required=False, label='Full Name')

    class Meta:
        model = User
        fields = ('email', 'full_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h3 class="mb-4">Create Your Account</h3>'),
            'full_name',
            'email',
            'password1',
            'password2',
            Div(
                Submit('submit', 'Sign Up', css_class='btn btn-primary btn-lg w-100'),
                css_class='d-grid gap-2'
            )
        )
        
        # Update field attributes
        self.fields['email'].widget.attrs.update({'class': 'form-control'})
        self.fields['full_name'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'class': 'form-control'})

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
        fields = [
            'full_name', 'date_of_birth', 
            'address', 'school_college_name', 'phone_number'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'address': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h3 class="mb-4">Profile Information</h3>'),
            HTML('<p class="text-muted mb-4">All fields are optional. You can update this information anytime.</p>'),
            'full_name',
            Row(
                Column('date_of_birth', css_class='form-group col-md-6 mb-3'),
                Column('phone_number', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            'school_college_name',
            'address',
            Div(
                Submit('submit', 'Update Profile', css_class='btn btn-primary'),
                css_class='d-grid gap-2 d-md-flex justify-content-md-end'
            )
        )
        
        # Update field attributes
        for field in self.fields.values():
            if 'class' not in field.widget.attrs:
                field.widget.attrs.update({'class': 'form-control'})
        
        # Update labels
        self.fields['full_name'].label = 'Full Name'
        self.fields['date_of_birth'].label = 'Date of Birth'
        self.fields['address'].label = 'Address'
        self.fields['school_college_name'].label = 'School/College Name'
        self.fields['phone_number'].label = 'Phone Number'

class CustomAuthenticationForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h3 class="mb-4">Welcome Back</h3>'),
            'username',  # Django's AuthenticationForm uses 'username' field
            'password',
            Div(
                Submit('submit', 'Sign In', css_class='btn btn-primary btn-lg w-100'),
                css_class='d-grid gap-2'
            )
        )
        
        # Customize the username field to work with email
        self.fields['username'].label = 'Email'
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Email',
            'type': 'email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })