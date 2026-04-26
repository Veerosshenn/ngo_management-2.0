# Topic 7: Enterprise Security Implementation

## Overview
This document details the multi-layered security implementation for the NGO Management System, focusing on **Defense in Depth** strategy beyond Django's built-in protections.

---

## 7.1 OWASP Top 10 Protection

### SQL Injection Prevention - Multi-Layer Approach

#### Layer 1: Django ORM (Built-in Protection) ✅
Django's ORM automatically uses **parameterized queries**, which separate SQL code from data:

```python
# SAFE - Django ORM parameterizes automatically
User.objects.filter(username=user_input)

# Generates: SELECT * FROM auth_user WHERE username = %s
# with parameters: [user_input]
```

#### Layer 2: Input Validation (Application Layer) ✅
**File: `accounts/validators.py`**

Implemented custom validators that scan for dangerous SQL patterns:

```python
class SQLInjectionValidator:
    SQL_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|TRUNCATE)\b)",
        r"(\b(UNION|JOIN|WHERE|FROM|INTO|VALUES|SET)\b.*\b(SELECT|INSERT|UPDATE|DELETE)\b)",
        r"(--|\#|\/\*|\*\/)",  # SQL comments
        r"(\b(OR|AND)\b\s+\d+\s*=\s*\d+)",  # OR 1=1 attacks
        r"(;\s*(SELECT|INSERT|UPDATE|DELETE|DROP))",  # Stacked queries
        r"(\bEXEC(\UTE)?\b)",  # EXEC/EXECUTE
        r"(\b(WAITFOR|DELAY|BENCHMARK|SLEEP)\b)",  # Time-based attacks
        r"(\b(INFORMATION_SCHEMA|SYSOBJECTS|SYSCOLUMNS)\b)",  # System tables
    ]
```

**Applied in Forms:**
- `accounts/forms.py`: Username, email, first_name, last_name validation
- `ngo/forms.py`: NGO name, description, contact_email, activity title, location validation

#### Layer 3: XSS Prevention ✅
**File: `accounts/validators.py`**

```python
class XSSValidator:
    XSS_PATTERNS = [
        r"(<\s*script)",  # Script tags
        r"(javascript\s*:)",  # JavaScript protocol
        r"(on\w+\s*=)",  # Event handlers (onclick, onload)
        r"(<\s*iframe)",  # iframe tags
        r"(<\s*svg.*on\w+)",  # SVG with events
    ]
```

#### Layer 4: Whitelist Approach ✅
**File: `accounts/validators.py`**

```python
class SafeCharacterValidator:
    """Only allows safe characters (whitelist approach)"""
    allowed_pattern = r'^[\w\s\-\.\@\,\(\)]+$'
```

#### Layer 5: Query Monitoring & Logging ✅
**File: `ngo_management/middleware/security.py`**

```python
class SQLQueryMonitoringMiddleware:
    """Monitors all SQL queries for suspicious patterns"""
    SUSPICIOUS_PATTERNS = [
        r"(\bOR\b\s+\d+\s*=\s*\d+)",  # OR 1=1
        r"(\bUNION\b.*\bSELECT\b)",  # UNION SELECT
        r"(--|\#|\/\*)",  # SQL comments
    ]
```

**Features:**
- Logs all SQL queries executed during a request
- Detects and warns about suspicious patterns
- Creates audit trail for security analysis
- Logs user, IP address, and request path for forensics

---

### CSRF Protection ✅

**Built-in Django Protection:**
- `CsrfViewMiddleware` enabled in `settings.py`
- CSRF tokens required in all POST forms
- CSRF cookie configured with `HTTPONLY` flag

**Implementation:**
```python
# In templates
{% csrf_token %}

# In settings.py
CSRF_COOKIE_HTTPONLY = True
```

---

### XSS Prevention ✅

**Multiple Layers:**
1. **Django Templates**: Auto-escape all variables by default
2. **Input Validation**: `XSSValidator` in forms
3. **Security Headers**: `SECURE_BROWSER_XSS_FILTER = True`

---

## 7.2 Secure Authentication & Sessions

### Session Security Configuration

**File: `ngo_management/settings.py`**

```python
# Session stored in database (more secure than cookies)
SESSION_ENGINE = 'django.contrib.sessions.backends.db'

# Session expires after 8 hours of inactivity
SESSION_COOKIE_AGE = 8 * 60 * 60  # 8 hours

# Session destroyed when browser closes
SESSION_EXPIRE_AT_BROWSER_CLOSE = True

# HTTP-only cookies (JavaScript cannot access)
SESSION_COOKIE_HTTPONLY = True
CSRF_COOKIE_HTTPONLY = True

# Secure cookies (HTTPS only) - for production
SESSION_COOKIE_SECURE = False  # Set True in production
CSRF_COOKIE_SECURE = False  # Set True in production
```

### Brute-Force Protection

**File: `accounts/views.py`**

```python
MAX_FAILED_ATTEMPTS = 5

def login_view(request):
    failed = request.session.get('login_failed_attempts', 0)
    
    if failed >= MAX_FAILED_ATTEMPTS:
        # Account locked
        messages.error(request, 'Too many failed attempts. Contact administrator.')
        return render(request, 'accounts/login.html', {'locked': True})
    
    # Increment counter on failure
    request.session['login_failed_attempts'] = failed + 1
```

**Features:**
- Tracks failed login attempts per session
- Locks account after 5 failed attempts
- Shows remaining attempts to user
- Resets counter on successful login

### Session Hijacking Prevention

**Implemented Measures:**
1. **Session Expiry**: 8-hour timeout
2. **Browser Close Expiry**: Sessions end when browser closes
3. **HTTP-Only Cookies**: JavaScript cannot steal session cookies
4. **Logout Functionality**: Proper session destruction on logout

```python
def logout_view(request):
    logout(request)  # Destroys server-side session
    messages.info(request, 'You have been logged out.')
    return redirect('accounts:login')
```

---

## 7.3 API Security

### Token Authentication (To be implemented in Topic 8)
- Django REST Framework Token Authentication
- Only authenticated users can access API endpoints
- Role-based permissions (Admin vs Employee)

### Role-Based Access Control (RBAC)

**File: `ngo_management/middleware.py`**

```python
class RoleBasedAccessMiddleware:
    """Ensures users can only access resources based on their role"""
    
    # Admin-only operations
    - Create/Edit/Delete NGOs
    - Create/Edit/Delete Activities
    
    # Employee-only operations
    - Register for activities
    - View own registrations
```

---

## 7.4 Secure Coding Practices

### Input Validation

**All Forms Include:**
- SQL Injection validation
- XSS validation
- Character whitelist validation
- Length validation
- Type validation

**Example:**
```python
def clean_username(self):
    username = self.cleaned_data.get('username', '')
    
    # SQL Injection check
    validator = SQLInjectionValidator()
    try:
        validator(username)
    except ValidationError:
        raise ValidationError("Username contains invalid characters.")
    
    # XSS check
    xss_validator = XSSValidator()
    try:
        xss_validator(username)
    except ValidationError:
        raise ValidationError("Username contains invalid characters.")
    
    return username
```

### Error Handling

**Principles:**
- No sensitive data in error messages
- No stack traces exposed to users
- Generic error messages for users
- Detailed logging for developers

**Example:**
```python
try:
    reg = Registration.objects.get(employee=request.user, activity_id=activity_id)
except Registration.DoesNotExist:
    messages.error(request, 'Registration not found.')  # Generic message
    # Detailed error logged internally
```

### Password Security

**File: `accounts/validators.py`**

```python
class PasswordComplexityValidator:
    """
    - Minimum 8 characters
    - At least one uppercase letter
    - At least one lowercase letter
    - At least one digit
    - At least one special character
    """
```

**Hashing:**
- Django uses PBKDF2-SHA256 by default
- Passwords never stored in plain text
- Salt automatically generated per password

---

## Security Testing

### Manual Testing Checklist

**SQL Injection Tests:**
```
Test Input: ' OR '1'='1
Expected: Rejected by SQLInjectionValidator

Test Input: '; DROP TABLE users; --
Expected: Rejected by SQLInjectionValidator

Test Input: admin'--
Expected: Rejected by SQLInjectionValidator
```

**XSS Tests:**
```
Test Input: <script>alert('XSS')</script>
Expected: Rejected by XSSValidator

Test Input: javascript:alert(1)
Expected: Rejected by XSSValidator

Test Input: <img src=x onerror=alert(1)>
Expected: Rejected by XSSValidator
```

**Session Security Tests:**
```
1. Login and wait 8 hours → Session should expire
2. Close browser → Session should be destroyed
3. Try to access session cookie via JavaScript → Should fail (HTTP-only)
4. Login with wrong password 5 times → Account should lock
```

---

## Files Modified

| File | Purpose |
|------|---------|
| `accounts/validators.py` | SQL Injection, XSS, Safe Character validators |
| `accounts/forms.py` | Applied validators to registration form |
| `ngo/forms.py` | Applied validators to NGO/Activity forms |
| `ngo_management/middleware/security.py` | SQL query monitoring middleware |
| `ngo_management/settings.py` | Security headers and session configuration |
| `accounts/views.py` | Brute-force protection (already implemented) |

---

## Summary

### What We Implemented Beyond Django ORM:

1. ✅ **Input Validation Layer** - Custom validators for SQL/XSS patterns
2. ✅ **Whitelist Approach** - Only allow safe characters
3. ✅ **Query Monitoring** - Log and detect suspicious queries
4. ✅ **Security Headers** - XSS filter, content-type protection
5. ✅ **Session Hardening** - HTTP-only cookies, expiry, brute-force protection
6. ✅ **Audit Logging** - Track all requests with user/IP info
7. ✅ **Error Handling** - No sensitive data exposure

### Defense in Depth Strategy:

```
User Input → Form Validation → ORM Parameterization → Database
     ↓              ↓                  ↓                  ↓
  XSS Check    SQL Injection      Parameterized     DB User
  SQL Check    Whitelist          Queries           Permissions
```

Each layer provides independent protection, so if one layer fails, others still protect the system.
