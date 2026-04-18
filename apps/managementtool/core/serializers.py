from rest_framework import serializers

from core.models import DeviceUpdate


class DeviceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceUpdate
        fields = "__all__"
