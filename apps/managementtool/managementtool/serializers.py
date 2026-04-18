from rest_framework import serializers

from managementtool.models import DeviceUpdate


class DeviceUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = DeviceUpdate
        fields = "__all__"
