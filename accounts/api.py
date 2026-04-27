from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response


@api_view(["GET"])
@permission_classes([IsAuthenticated])
def me(request):
    """
    Topic 11: User Service endpoint for gateway/service-to-service checks.
    """
    u = request.user
    return Response(
        {
            "id": u.id,
            "username": u.username,
            "email": u.email,
            "role": getattr(u, "role", None),
            "is_admin": bool(getattr(u, "is_admin", False) or (callable(getattr(u, "is_admin", None)) and u.is_admin())),
            "is_employee": bool(
                getattr(u, "is_employee", False) or (callable(getattr(u, "is_employee", None)) and u.is_employee())
            ),
        }
    )

