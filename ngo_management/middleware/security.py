"""
ngo_management/middleware/security.py

Topic 7.1: SQL Injection Prevention - Query Monitoring Layer
Topic 7.4: Secure Coding - Security Logging

Middleware for monitoring and logging database queries to detect
potential SQL injection attempts.
"""

import re
import time
import logging
from django.conf import settings
from django.db import connection
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)


class SQLQueryMonitoringMiddleware(MiddlewareMixin):
    """
    Monitors SQL queries for potential injection attempts.
    Logs suspicious patterns for security auditing.
    """
    
    # Patterns that might indicate SQL injection attempts
    SUSPICIOUS_PATTERNS = [
        r"(\bOR\b\s+\d+\s*=\s*\d+)",  # OR 1=1
        r"(\bUNION\b.*\bSELECT\b)",  # UNION SELECT
        r"(--|\#|\/\*)",  # SQL comments
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


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Enhanced request logging with security focus.
    Topic 7.4: Secure Coding - Audit Trail
    """
    
    def process_request(self, request):
        """Log incoming requests"""
        logger.info(
            f"REQUEST: {request.method} {request.path}",
            extra={
                'user': getattr(request.user, 'username', 'anonymous'),
                'ip_address': self._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', 'unknown')[:100],
            }
        )
        return None
    
    def _get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
