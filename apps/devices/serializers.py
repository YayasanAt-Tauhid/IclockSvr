"""
API Serializers for Device Management
"""
from rest_framework import serializers
from .models import Device, DeviceUser, DeviceLog


class DeviceSerializer(serializers.ModelSerializer):
    """Serializer for Device model"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Device
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'last_online']


class DeviceUserSerializer(serializers.ModelSerializer):
    """Serializer for DeviceUser model"""
    user_username = serializers.CharField(source='user.username', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = DeviceUser
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'synced_at']


class DeviceLogSerializer(serializers.ModelSerializer):
    """Serializer for DeviceLog model"""
    device_name = serializers.CharField(source='device.name', read_only=True)
    
    class Meta:
        model = DeviceLog
        fields = '__all__'
        read_only_fields = ['timestamp']
