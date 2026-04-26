from rest_framework import serializers
from .models import Registration
from ngo.models import Activity
from registration.services import RegistrationService


class RegistrationSerializer(serializers.ModelSerializer):
    employee = serializers.SlugRelatedField(read_only=True, slug_field='username')
    activity = serializers.PrimaryKeyRelatedField(queryset=Activity.objects.all())

    class Meta:
        model = Registration
        fields = ('id', 'employee', 'activity', 'registered_at', 'status')
        read_only_fields = ('id', 'employee', 'registered_at', 'status')

    def create(self, validated_data):
        request = self.context.get('request')
        user = getattr(request, 'user', None)
        if user is None or not user.is_authenticated:
            raise serializers.ValidationError('Authentication required')

        activity = validated_data['activity']
        # Use service layer to handle concurrency and business rules
        try:
            reg = RegistrationService.register_user(user, activity.id)
        except ValueError as e:
            # Convert business-rule violations into a proper 400 JSON response
            raise serializers.ValidationError({'detail': str(e)})
        return reg
