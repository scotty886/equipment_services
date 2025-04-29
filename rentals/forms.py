from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, SetPasswordForm
from django import forms

import logging

# Create a logger
logger = logging.getLogger(__name__)

class PasswordChangeForm(SetPasswordForm):
    class Meta:
        model = User
        fields = ('new_password1', 'new_password2')

    def __init__(self, *args, **kwargs):
        super(PasswordChangeForm, self).__init__(*args, **kwargs)

        self.fields['new_password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password1'].widget.attrs.update({'placeholder': 'New Password'})
        self.fields['new_password1'].label = ''
        self.fields['new_password1'].help_text = '<span class="form-text text-muted">Your password can’t be too similar to your other personal information.</span>'

        self.fields['new_password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['new_password2'].widget.attrs.update({'placeholder': 'Confirm New Password'})
        self.fields['new_password2'].label = ''
        self.fields['new_password2'].help_text = '<span class="form-text text-muted">Enter the same password as before, for verification.</span>'

class UpdateUserForm(UserChangeForm):
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    first_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))

class SignUpForm(UserCreationForm):
    logger.error("SignUpForm initialized")
    email = forms.EmailField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email'}))
    first_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'}))
    last_name = forms.CharField(label="", widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'}))

    class Meta:
        logger.error("Meta class initialized")
        model = User
        fields = ('username', 'email', 'first_name', 'last_name', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)
        logger.error("SignUpForm __init__ method called")
        self.fields['username'].widget.attrs.update({'class': 'form-control'})
        self.fields["username"].widget.attrs["placeholder"] = "Pick a User Name"
        self.fields['username'].label = ''
        self.fields[
            'username'].help_text = '<span class="form-text text-muted">Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</span>'

        self.fields['password1'].widget.attrs.update({'class': 'form-control'})
        self.fields['password1'].widget.attrs.update({'placeholder': 'Password'})
        self.fields['password1'].label = ''
        self.fields[
            'password1'].help_text = '<span class="form-text text-muted">Your password can’t be too similar to your other personal information.</span>'

        self.fields['password2'].widget.attrs.update({'class': 'form-control'})
        self.fields['password2'].widget.attrs.update({'placeholder': 'Confirm Password'})
        self.fields['password2'].label = ''
        self.fields[
            'password2'].help_text = '<span class="form-text text-muted">Enter the same password as before, for verification.</span>'