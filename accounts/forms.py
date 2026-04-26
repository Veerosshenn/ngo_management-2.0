"""
accounts/forms.py

Topic 6.2 / 6.5 – Session Management & Enterprise Auth Best Practices
Topic 6.3      – Password Hashing (enforced via Django validators)
Topic 5.3      – Form-level validation for data integrity
"""

import re
from django.contrib.auth.forms import AuthenticationForm
from django import forms
from django.core.exceptions import ValidationError
from accounts.models import CustomUser
from accounts.validators import SQLInjectionValidator, XSSValidator, SafeCharacterValidator


class LoginForm(AuthenticationForm):
    username = forms.CharField(
        widget=forms.TextInput(attrs={
            'class': 'form-input',
            'placeholder': 'Username',
            'autofocus': True,
            'id': 'id_login_username',
        })
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'id': 'id_login_password',
        })
    )


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Password',
            'id': 'id_reg_password1',
        }),
        help_text=(
            'Must be at least 8 characters and contain an uppercase letter, '
            'a lowercase letter, a digit, and a special character.'
        ),
    )
    password2 = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput(attrs={
            'class': 'form-input',
            'placeholder': 'Confirm Password',
            'id': 'id_reg_password2',
        }),
    )

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'first_name', 'last_name', 'role']
        widgets = {
            'username':   forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Username'}),
            'email':      forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'Email'}),
            'first_name': forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'First Name'}),
            'last_name':  forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Last Name'}),
            'role':       forms.Select(attrs={'class': 'form-input'}),
        }

    def clean_username(self):
        """Topic 7.1 & 7.4: SQL Injection & XSS Prevention"""
        username = self.cleaned_data.get('username', '')
        # Apply SQL injection validation
        validator = SQLInjectionValidator()
        try:
            validator(username)
        except ValidationError:
            raise ValidationError("Username contains invalid characters.")
        
        # Apply XSS validation
        xss_validator = XSSValidator()
        try:
            xss_validator(username)
        except ValidationError:
            raise ValidationError("Username contains invalid characters.")
        
        return username
    
    def clean_email(self):
        """Topic 7.1 & 7.4: SQL Injection & XSS Prevention for Email"""
        email = self.cleaned_data.get('email', '')
        # Apply SQL injection validation
        validator = SQLInjectionValidator()
        try:
            validator(email)
        except ValidationError:
            raise ValidationError("Email contains invalid characters.")
        
        return email
    
    def clean_first_name(self):
        """Topic 7.1 & 7.4: Input Validation for First Name"""
        first_name = self.cleaned_data.get('first_name', '')
        # Apply safe character validation (whitelist approach)
        validator = SafeCharacterValidator(
            allowed_pattern=r'^[\w\s\-\'\.]+$',
            message="First name contains invalid characters."
        )
        try:
            validator(first_name)
        except ValidationError:
            raise ValidationError("First name contains invalid characters.")
        
        return first_name
    
    def clean_last_name(self):
        """Topic 7.1 & 7.4: Input Validation for Last Name"""
        last_name = self.cleaned_data.get('last_name', '')
        # Apply safe character validation
        validator = SafeCharacterValidator(
            allowed_pattern=r'^[\w\s\-\'\.]+$',
            message="Last name contains invalid characters."
        )
        try:
            validator(last_name)
        except ValidationError:
            raise ValidationError("Last name contains invalid characters.")
        
        return last_name
    
    #  6.3: password complexity validation ──────────────────────
    def clean_password1(self):
        password = self.cleaned_data.get('password1', '')
        errors = []
        if len(password) < 8:
            errors.append('at least 8 characters')
        if not re.search(r'[A-Z]', password):
            errors.append('one uppercase letter (A–Z)')
        if not re.search(r'[a-z]', password):
            errors.append('one lowercase letter (a–z)')
        if not re.search(r'\d', password):
            errors.append('one digit (0–9)')
        if not re.search(r'[!@#$%^&*()\-_=+\[\]{};\':\"\\|,.<>/?]', password):
            errors.append('one special character (!@#$%^&* etc.)')
        if errors:
            raise ValidationError(
                f"Password must contain: {', '.join(errors)}."
            )
        return password

    def clean_password2(self):
        p1 = self.cleaned_data.get('password1')
        p2 = self.cleaned_data.get('password2')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Passwords do not match.')
        return p2

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user
