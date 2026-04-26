"""
accounts/validators.py

Topic 6.3 / 6.5 – Password Hashing & Enterprise Auth Best Practices
---------------------------------------------------------------------
Custom password validator that enforces complexity rules suitable for an
enterprise environment: the password must contain at least one uppercase
letter, one lowercase letter, one digit, and one special character.
"""

import re
from django.core.exceptions import ValidationError
from django.utils.deconstruct import deconstructible
from django.utils.translation import gettext as _


class PasswordComplexityValidator:
    """
    Validates that the password meets complexity requirements:
    - At least 8 characters long (handled by Django's MinimumLengthValidator)
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character  (!@#$%^&*…)
    """

    def validate(self, password, user=None):
        errors = []
        if not re.search(r'[A-Z]', password):
            errors.append(_("at least one uppercase letter (A–Z)"))
        if not re.search(r'[a-z]', password):
            errors.append(_("at least one lowercase letter (a–z)"))
        if not re.search(r'\d', password):
            errors.append(_("at least one digit (0–9)"))
        if not re.search(r'[!@#$%^&*()_+\-=\[\]{};\':\"\\|,.<>\/?]', password):
            errors.append(_("at least one special character (!@#$%^&* etc.)"))
        if errors:
            raise ValidationError(
                _("Your password must contain %(reqs)s."),
                code='password_too_simple',
                params={'reqs': ', '.join(errors)},
            )

    def get_help_text(self):
        return _(
            "Your password must contain at least one uppercase letter, "
            "one lowercase letter, one digit, and one special character."
        )


@deconstructible
class SQLInjectionValidator:
    """
    Topic 7.1: SQL Injection Prevention - Input Validation Layer
    Topic 7.4: Secure Coding - Input Sanitization
    
    Validates that input doesn't contain SQL injection patterns.
    Adds defense-in-depth beyond Django ORM parameterization.
    """
    
    # Dangerous SQL patterns to block
    SQL_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b)",
        r"(\b(UNION|JOIN|WHERE|FROM|INTO|VALUES|SET)\b.*\b(SELECT|INSERT|UPDATE|DELETE)\b)",
        r"(--|#|/[*]|[*]/)",  # SQL comments
        r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",  # OR 1=1, AND 1=1
        r"(\b(OR|AND)\b\s+['\"]?\w+['\"]?\s*=\s*['\"]?\w+['\"]?)",  # OR 'a'='a'
        r"(;\s*(SELECT|INSERT|UPDATE|DELETE|DROP))",  # Stacked queries
        r"(\bEXEC(UTE)?\b)",  # EXEC/EXECUTE
        r"(\b(WAITFOR|DELAY|BENCHMARK|SLEEP)\b)",  # Time-based attacks
        r"(\b(INFORMATION_SCHEMA|SYSOBJECTS|SYSCOLUMNS)\b)",  # System tables
    ]
    
    def __init__(self, message=None):
        self.message = message or "Input contains potentially dangerous SQL patterns."
    
    def __call__(self, value):
        if not isinstance(value, str):
            return
        
        value_upper = value.upper()
        for pattern in self.SQL_PATTERNS:
            if re.search(pattern, value_upper, re.IGNORECASE):
                raise ValidationError(self.message)


@deconstructible
class XSSValidator:
    """
    Topic 7.1: OWASP Top 10 - XSS Prevention
    Validates that input doesn't contain Cross-Site Scripting patterns.
    """
    
    XSS_PATTERNS = [
        r"(<\s*script)",  # Script tags
        r"(javascript\s*:)",  # JavaScript protocol
        r"(on\w+\s*=)",  # Event handlers (onclick, onload, etc.)
        r"(<\s*iframe)",  # iframe tags
        r"(<\s*svg.*on\w+)",  # SVG with events
    ]
    
    def __init__(self, message=None):
        self.message = message or "Input contains potentially dangerous XSS patterns."
    
    def __call__(self, value):
        if not isinstance(value, str):
            return
        
        value_lower = value.lower()
        for pattern in self.XSS_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                raise ValidationError(self.message)


@deconstructible
class SafeCharacterValidator:
    """
    Topic 7.4: Secure Coding - Whitelist Input Validation
    Only allows safe characters based on regex pattern.
    """
    
    def __init__(self, allowed_pattern=r'^[\w\s\-\.\@\,\(\)]+$', message=None):
        self.allowed_pattern = allowed_pattern
        self.message = message or "Input contains invalid characters."
    
    def __call__(self, value):
        if not isinstance(value, str):
            return
        
        if not re.match(self.allowed_pattern, value):
            raise ValidationError(self.message)
