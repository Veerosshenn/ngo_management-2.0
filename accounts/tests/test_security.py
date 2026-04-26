"""
accounts/tests/test_security.py

Topic 7.1: Security Testing - SQL Injection & XSS Prevention
Topic 7.4: Secure Coding - Input Validation Testing
Topic 13.1: Unit Testing

Test suite to verify security implementations.
"""

from django.test import TestCase
from django.core.exceptions import ValidationError
from accounts.validators import (
    SQLInjectionValidator,
    XSSValidator,
    SafeCharacterValidator,
)
from accounts.forms import RegisterForm
from ngo.forms import NGOForm, ActivityForm


class SQLInjectionValidatorTest(TestCase):
    """Test SQL Injection Prevention"""
    
    def setUp(self):
        self.validator = SQLInjectionValidator()
    
    def test_safe_input(self):
        """Safe input should pass validation"""
        safe_inputs = [
            "john_doe",
            "John Doe",
            "john@example.com",
            "NGO Name",
            "Activity Description",
        ]
        for value in safe_inputs:
            try:
                self.validator(value)
            except ValidationError:
                self.fail(f"Safe input '{value}' was incorrectly rejected")
    
    def test_sql_keywords_blocked(self):
        """SQL keywords should be blocked"""
        dangerous_inputs = [
            "SELECT * FROM users",
            "DROP TABLE users",
            "INSERT INTO users VALUES",
            "DELETE FROM users",
            "UPDATE users SET",
        ]
        for value in dangerous_inputs:
            with self.assertRaises(ValidationError):
                self.validator(value)
    
    def test_sql_comments_blocked(self):
        """SQL comments should be blocked"""
        dangerous_inputs = [
            "admin'--",
            "admin#comment",
            "admin/*comment*/",
        ]
        for value in dangerous_inputs:
            with self.assertRaises(ValidationError):
                self.validator(value)
    
    def test_union_select_blocked(self):
        """UNION SELECT attacks should be blocked"""
        dangerous_inputs = [
            "' UNION SELECT * FROM users--",
            "1 UNION SELECT password FROM users",
        ]
        for value in dangerous_inputs:
            with self.assertRaises(ValidationError):
                self.validator(value)
    
    def test_or_injection_blocked(self):
        """OR-based injection should be blocked"""
        dangerous_inputs = [
            "' OR '1'='1",
            "admin' OR 1=1--",
            "' OR 'a'='a",
        ]
        for value in dangerous_inputs:
            with self.assertRaises(ValidationError):
                self.validator(value)
    
    def test_stacked_queries_blocked(self):
        """Stacked queries should be blocked"""
        dangerous_inputs = [
            "'; DROP TABLE users;--",
            "admin'; DELETE FROM users;--",
        ]
        for value in dangerous_inputs:
            with self.assertRaises(ValidationError):
                self.validator(value)
    
    def test_time_based_attacks_blocked(self):
        """Time-based blind SQL injection should be blocked"""
        dangerous_inputs = [
            "'; WAITFOR DELAY '0:0:5'--",
            "admin' AND SLEEP(5)--",
            "1; BENCHMARK(1000000,SHA1('test'))--",
        ]
        for value in dangerous_inputs:
            with self.assertRaises(ValidationError):
                self.validator(value)
    
    def test_system_tables_blocked(self):
        """System table access should be blocked"""
        dangerous_inputs = [
            "INFORMATION_SCHEMA.TABLES",
            "SYSOBJECTS",
            "SYSCOLUMNS",
        ]
        for value in dangerous_inputs:
            with self.assertRaises(ValidationError):
                self.validator(value)


class XSSValidatorTest(TestCase):
    """Test XSS Prevention"""
    
    def setUp(self):
        self.validator = XSSValidator()
    
    def test_safe_input(self):
        """Safe input should pass validation"""
        safe_inputs = [
            "Hello World",
            "This is a description",
            "john@example.com",
        ]
        for value in safe_inputs:
            try:
                self.validator(value)
            except ValidationError:
                self.fail(f"Safe input '{value}' was incorrectly rejected")
    
    def test_script_tags_blocked(self):
        """Script tags should be blocked"""
        dangerous_inputs = [
            "<script>alert('XSS')</script>",
            "<script>document.cookie</script>",
            "<SCRIPT>alert(1)</SCRIPT>",
        ]
        for value in dangerous_inputs:
            with self.assertRaises(ValidationError):
                self.validator(value)
    
    def test_javascript_protocol_blocked(self):
        """JavaScript protocol should be blocked"""
        dangerous_inputs = [
            "javascript:alert(1)",
            "JAVASCRIPT:void(0)",
        ]
        for value in dangerous_inputs:
            with self.assertRaises(ValidationError):
                self.validator(value)
    
    def test_event_handlers_blocked(self):
        """Event handlers should be blocked"""
        dangerous_inputs = [
            "onmouseover=alert(1)",
            "onclick=alert('XSS')",
            "onload=alert(document.cookie)",
        ]
        for value in dangerous_inputs:
            with self.assertRaises(ValidationError):
                self.validator(value)
    
    def test_iframe_blocked(self):
        """iframe tags should be blocked"""
        dangerous_inputs = [
            "<iframe src='http://evil.com'></iframe>",
            "<IFRAME src='javascript:alert(1)'></IFRAME>",
        ]
        for value in dangerous_inputs:
            with self.assertRaises(ValidationError):
                self.validator(value)


class SafeCharacterValidatorTest(TestCase):
    """Test Whitelist Character Validation"""
    
    def test_allowed_characters(self):
        """Allowed characters should pass"""
        validator = SafeCharacterValidator()
        safe_inputs = [
            "John Doe",
            "john_doe",
            "test@example.com",
            "NGO-Name",
            "Activity (2026)",
        ]
        for value in safe_inputs:
            try:
                validator(value)
            except ValidationError:
                self.fail(f"Safe input '{value}' was incorrectly rejected")
    
    def test_special_characters_blocked(self):
        """Special characters should be blocked"""
        validator = SafeCharacterValidator()
        dangerous_inputs = [
            "admin<script>",
            "user;DROP TABLE",
            "test' OR '1'='1",
        ]
        for value in dangerous_inputs:
            with self.assertRaises(ValidationError):
                validator(value)


class FormSecurityTest(TestCase):
    """Test Security Validators in Forms"""
    
    def test_register_form_sql_injection(self):
        """Registration form should reject SQL injection"""
        invalid_data = {
            'username': "admin' OR '1'='1",
            'email': "test@example.com",
            'first_name': "John",
            'last_name': "Doe",
            'password1': "SecurePass123!",
            'password2': "SecurePass123!",
        }
        form = RegisterForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('username', form.errors)
    
    def test_register_form_xss(self):
        """Registration form should reject XSS"""
        invalid_data = {
            'username': "<script>alert(1)</script>",
            'email': "test@example.com",
            'first_name': "John",
            'last_name': "Doe",
            'password1': "SecurePass123!",
            'password2': "SecurePass123!",
        }
        form = RegisterForm(data=invalid_data)
        self.assertFalse(form.is_valid())
    
    def test_ngo_form_sql_injection(self):
        """NGO form should reject SQL injection"""
        invalid_data = {
            'name': "NGO'; DROP TABLE users;--",
            'description': "Valid description",
            'website': "https://ngo.org",
            'contact_email': "contact@ngo.org",
        }
        form = NGOForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_activity_form_xss(self):
        """Activity form should reject XSS"""
        invalid_data = {
            'title': "<script>alert('XSS')</script>",
            'description': "Valid description",
            'location': "Kuala Lumpur",
            'date': "2026-05-01T10:00",
            'cut_off_datetime': "2026-04-30T23:59",
            'max_slots': 50,
            'ngo': 1,
        }
        form = ActivityForm(data=invalid_data)
        self.assertFalse(form.is_valid())
        self.assertIn('title', form.errors)


class SecurityIntegrationTest(TestCase):
    """Integration tests for security features"""
    
    def test_valid_registration(self):
        """Valid registration should succeed"""
        valid_data = {
            'username': "john_doe",
            'email': "john@example.com",
            'first_name': "John",
            'last_name': "Doe",
            'role': "employee",
            'password1': "SecurePass123!",
            'password2': "SecurePass123!",
        }
        form = RegisterForm(data=valid_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
    
    def test_valid_ngo_creation(self):
        """Valid NGO creation should succeed"""
        valid_data = {
            'name': "Helping Hands NGO",
            'description': "We help communities in need.",
            'website': "https://helpinghands.org",
            'contact_email': "contact@helpinghands.org",
        }
        form = NGOForm(data=valid_data)
        self.assertTrue(form.is_valid(), f"Form errors: {form.errors}")
