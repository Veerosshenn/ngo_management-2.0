from rest_framework.permissions import BasePermission, SAFE_METHODS


class IsAdminOrReadOnly(BasePermission):
    """Allow read-only to authenticated users; write only for admins."""

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return request.user and request.user.is_authenticated
        return request.user and request.user.is_authenticated and request.user.is_admin()


class IsAdmin(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_admin()


class IsEmployee(BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated and request.user.is_employee()
