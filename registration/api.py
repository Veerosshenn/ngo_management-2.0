from rest_framework import viewsets, status, mixins
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from accounts.api_permissions import IsEmployee
from django.core.cache import cache
from .models import Registration
from .serializers import RegistrationSerializer


class RegistrationViewSet(
    mixins.CreateModelMixin,
    mixins.DestroyModelMixin,
    mixins.ListModelMixin,
    mixins.RetrieveModelMixin,
    viewsets.GenericViewSet,
):
    queryset = Registration.objects.select_related('activity').all()
    serializer_class = RegistrationSerializer
    permission_classes = [IsAuthenticated, IsEmployee]

    def get_queryset(self):
        # Employees should only see/manage their own registrations
        qs = super().get_queryset()
        user = getattr(self.request, "user", None)
        if user and user.is_authenticated:
            return qs.filter(employee=user)
        return qs.none()

    def _bump_participants_cache(self, activity_id: int):
        version_key = f"api:v1:activity:{activity_id}:participants:version"
        try:
            cache.incr(version_key)
        except ValueError:
            cache.set(version_key, 2, timeout=None)

    def perform_create(self, serializer):
        reg = serializer.save()
        self._bump_participants_cache(reg.activity_id)
        return reg

    def destroy(self, request, pk=None):
        # Cancel registration
        try:
            reg = self.get_queryset().get(pk=pk)
        except Registration.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if reg.status != 'active':
            return Response({'detail': 'Registration already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

        reg.status = 'cancelled'
        reg.save(update_fields=['status'])
        self._bump_participants_cache(reg.activity_id)
        return Response({'detail': 'Cancelled.'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['delete'], url_path=r'by-activity/(?P<activity_id>\d+)')
    def cancel_by_activity(self, request, activity_id=None):
        """
        Convenience cancellation endpoint:
        DELETE /api/v1/registrations/by-activity/<activity_id>/
        """
        try:
            reg = self.get_queryset().get(activity_id=activity_id)
        except Registration.DoesNotExist:
            return Response({'detail': 'Not found.'}, status=status.HTTP_404_NOT_FOUND)

        if reg.status != 'active':
            return Response({'detail': 'Registration already cancelled.'}, status=status.HTTP_400_BAD_REQUEST)

        reg.status = 'cancelled'
        reg.save(update_fields=['status'])
        self._bump_participants_cache(reg.activity_id)
        return Response({'detail': 'Cancelled.'}, status=status.HTTP_200_OK)
