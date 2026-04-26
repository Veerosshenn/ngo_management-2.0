"""
ngo/forms.py

Topic 5.3 – Validation and Data Integrity (form-level)
Topic 7.1 & 7.4 – SQL Injection & XSS Prevention (input validation)
"""

from django import forms
from django.core.exceptions import ValidationError
from ngo.models import NGO, Activity
from accounts.validators import SQLInjectionValidator, XSSValidator, SafeCharacterValidator


class NGOForm(forms.ModelForm):
    class Meta:
        model = NGO
        fields = ['name', 'description', 'website', 'contact_email']
        widgets = {
            'name':          forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'NGO Name'}),
            'description':   forms.Textarea(attrs={'class': 'form-input', 'rows': 3, 'placeholder': 'Brief description'}),
            'website':       forms.URLInput(attrs={'class': 'form-input', 'placeholder': 'https://...'}),
            'contact_email': forms.EmailInput(attrs={'class': 'form-input', 'placeholder': 'contact@ngo.org'}),
        }
    
    def clean_name(self):
        """Topic 7.1 & 7.4: SQL Injection & XSS Prevention for NGO Name"""
        name = self.cleaned_data.get('name', '')
        # Apply SQL injection validation
        validator = SQLInjectionValidator()
        try:
            validator(name)
        except ValidationError:
            raise ValidationError("NGO name contains invalid characters.")
        
        # Apply XSS validation
        xss_validator = XSSValidator()
        try:
            xss_validator(name)
        except ValidationError:
            raise ValidationError("NGO name contains invalid characters.")
        
        return name
    
    def clean_description(self):
        """Topic 7.1 & 7.4: Input Validation for Description"""
        description = self.cleaned_data.get('description', '')
        # Apply SQL injection validation
        validator = SQLInjectionValidator()
        try:
            validator(description)
        except ValidationError:
            raise ValidationError("Description contains invalid characters.")
        
        return description
    
    def clean_contact_email(self):
        """Topic 7.1 & 7.4: Input Validation for Contact Email"""
        email = self.cleaned_data.get('contact_email', '')
        # Apply SQL injection validation
        validator = SQLInjectionValidator()
        try:
            validator(email)
        except ValidationError:
            raise ValidationError("Email contains invalid characters.")
        
        return email


class ActivityForm(forms.ModelForm):
    class Meta:
        model = Activity
        fields = ['ngo', 'title', 'description', 'location', 'date', 'cut_off_datetime', 'max_slots']
        widgets = {
            'ngo':              forms.Select(attrs={'class': 'form-input'}),
            'title':            forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Activity Title'}),
            'description':      forms.Textarea(attrs={'class': 'form-input', 'rows': 4, 'placeholder': 'Description'}),
            'location':         forms.TextInput(attrs={'class': 'form-input', 'placeholder': 'Location'}),
            'date':             forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'cut_off_datetime': forms.DateTimeInput(attrs={'class': 'form-input', 'type': 'datetime-local'}, format='%Y-%m-%dT%H:%M'),
            'max_slots':        forms.NumberInput(attrs={'class': 'form-input', 'min': 1}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['cut_off_datetime'].input_formats = ['%Y-%m-%dT%H:%M']
        self.fields['ngo'].empty_label = '— Select NGO —'

    # Topic 5.3 – form-level validation
    def clean(self):
        cleaned_data = super().clean()
        date = cleaned_data.get('date')
        cutoff = cleaned_data.get('cut_off_datetime')
        if date and cutoff and cutoff >= date:
            raise forms.ValidationError(
                "Registration cut-off must be before the activity date."
            )
        return cleaned_data

    def clean_title(self):
        """Topic 7.1 & 7.4: SQL Injection & XSS Prevention for Activity Title"""
        title = (self.cleaned_data.get('title') or '').strip()
        # Template injection prevention
        if '{{' in title or '}}' in title or '{%' in title or '%}' in title:
            raise forms.ValidationError("Enter a normal activity title.")
        
        # Apply SQL injection validation
        validator = SQLInjectionValidator()
        try:
            validator(title)
        except ValidationError:
            raise forms.ValidationError("Activity title contains invalid characters.")
        
        # Apply XSS validation
        xss_validator = XSSValidator()
        try:
            xss_validator(title)
        except ValidationError:
            raise forms.ValidationError("Activity title contains invalid characters.")
        
        return title
    
    def clean_description(self):
        """Topic 7.1 & 7.4: Input Validation for Activity Description"""
        description = self.cleaned_data.get('description', '')
        # Apply SQL injection validation
        validator = SQLInjectionValidator()
        try:
            validator(description)
        except ValidationError:
            raise forms.ValidationError("Description contains invalid characters.")
        
        return description
    
    def clean_location(self):
        """Topic 7.1 & 7.4: Input Validation for Location"""
        location = self.cleaned_data.get('location', '')
        # Apply safe character validation
        validator = SafeCharacterValidator(
            allowed_pattern=r'^[\w\s\-\.\,\(\)]+$',
            message="Location contains invalid characters."
        )
        try:
            validator(location)
        except ValidationError:
            raise forms.ValidationError("Location contains invalid characters.")
        
        return location
