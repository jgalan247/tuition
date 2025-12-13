from django import forms
from .models import User, ContactMessage


class ContactForm(forms.ModelForm):
    """Contact form."""

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'phone', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Your name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-input',
                'placeholder': 'your@email.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Phone number (optional)'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-input',
                'placeholder': 'Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-textarea',
                'placeholder': 'Your message...',
                'rows': 5
            }),
        }


class ProfileForm(forms.ModelForm):
    """User profile edit form."""

    class Meta:
        model = User
        fields = [
            'first_name', 'last_name', 'phone',
            'parent_name', 'parent_email', 'parent_phone',
            'school', 'year_group', 'bio', 'profile_image',
            'preferred_delivery'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={'class': 'form-input'}),
            'last_name': forms.TextInput(attrs={'class': 'form-input'}),
            'phone': forms.TextInput(attrs={'class': 'form-input'}),
            'parent_name': forms.TextInput(attrs={'class': 'form-input'}),
            'parent_email': forms.EmailInput(attrs={'class': 'form-input'}),
            'parent_phone': forms.TextInput(attrs={'class': 'form-input'}),
            'school': forms.TextInput(attrs={'class': 'form-input'}),
            'year_group': forms.TextInput(attrs={'class': 'form-input'}),
            'bio': forms.Textarea(attrs={'class': 'form-textarea', 'rows': 3}),
            'preferred_delivery': forms.Select(attrs={'class': 'form-select'}),
        }


class SignupForm(forms.Form):
    """Extended signup form for django-allauth."""

    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    phone = forms.CharField(max_length=20, required=False)

    def signup(self, request, user):
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        user.phone = self.cleaned_data.get('phone', '')
        user.save()
