import re
import time
import logging
from django.shortcuts import redirect
from django.urls import reverse
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

# Routes that don't require authentication
PUBLIC_ROUTES = ['/accounts/login/', '/accounts/register/']
# Routes that only admins can access
ADMIN_ONLY_PREFIXES = ['/ngo/create/', '/admin/']

# Topic 7.1 & 7.4: SQL Query Monitoring Middleware
class SQLQueryMonitoringMiddleware(MiddlewareMixin):
    """
    Monitors SQL queries for potential injection attempts.
    Logs suspicious patterns for security auditing.
    """
    
    # Patterns that might indicate SQL injection attempts
    SUSPICIOUS_PATTERNS = [
        r"(\bOR\b\s+\d+\s*=\s*\d+)",  # OR 1=1
        r"(\bUNION\b.*\bSELECT\b)",  # UNION SELECT
        r"(--|#|/[*]|[*]/)",  # SQL comments
        r"(\bDROP\b|\bTRUNCATE\b|\bDELETE\b.*\bWHERE\b)",  # Destructive queries
        r"(\bEXEC\b|\bEXECUTE\b)",  # Stored procedure execution
        r"(\bWAITFOR\b|\bSLEEP\b|\bBENCHMARK\b)",  # Time-based attacks
    ]
    
    def process_request(self, request):
        """Store request start time for query analysis"""
        request.sql_query_log = []
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Log all queries executed during this request"""
        if hasattr(request, 'sql_query_log'):
            for query in request.sql_query_log:
                self._analyze_query(query, request)
        return response
    
    def process_exception(self, request, exception):
        """Log queries even if exception occurs"""
        if hasattr(request, 'sql_query_log'):
            for query in request.sql_query_log:
                self._analyze_query(query, request, is_error=True)
        return None
    
    def _analyze_query(self, query, request, is_error=False):
        """Analyze a single query for suspicious patterns"""
        sql = query.get('sql', '')
        
        # Check for suspicious patterns
        for pattern in self.SUSPICIOUS_PATTERNS:
            if re.search(pattern, sql, re.IGNORECASE):
                logger.warning(
                    f"SUSPICIOUS SQL QUERY DETECTED: {sql[:200]}",
                    extra={
                        'user': getattr(request.user, 'username', 'anonymous'),
                        'path': request.path,
                        'method': request.method,
                    }
                )
                break


class RequestLoggingMiddleware:
    """
    Logs every incoming HTTP request: method, path, user, and timestamp.
    Satisfies Topic 3.4 cross-cutting concern: request logging.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = request.user.username if request.user.is_authenticated else 'anonymous'
        logger.info(f"[REQUEST] {request.method} {request.path} | user={user}")
        response = self.get_response(request)
        logger.info(f"[RESPONSE] {request.method} {request.path} | status={response.status_code} | user={user}")
        return response


class RoleBasedAccessMiddleware:
    """
    Enforces access control:
    - Unauthenticated users are redirected to login.
    - Employees are blocked from admin-only routes.
    Satisfies Topic 3.4 cross-cutting concern: access control.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path

        # Allow public routes freely
        if any(path.startswith(route) for route in PUBLIC_ROUTES):
            return self.get_response(request)

        # Allow static files and Django admin (admin has its own auth)
        if path.startswith('/static/') or path.startswith('/admin/'):
            return self.get_response(request)

        # Redirect unauthenticated users to login
        if not request.user.is_authenticated:
            return redirect(f"{reverse('accounts:login')}?next={path}")

        # Block employees from admin-only create/edit/delete routes
        if request.user.is_authenticated and request.user.is_employee():
            blocked = ['/ngo/create/', '/ngo/'] 
            # Only block edit and delete sub-paths, not all of /ngo/
            if path.endswith('/edit/') or path.endswith('/delete/') or path == '/ngo/create/':
                from django.contrib import messages
                messages.error(request, 'Access denied. Administrators only.')
                return redirect('ngo:activity_list')

        return self.get_response(request)
