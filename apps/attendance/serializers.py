"""
API Serializers for Attendance Management
"""
from rest_framework import serializers
from .models import AttendanceRecord, DailyAttendance, LeaveRequest


class AttendanceRecordSerializer(serializers.ModelSerializer):
    """Serializer for AttendanceRecord"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    device_name = serializers.CharField(source='device.name', read_only=True)
    verify_type_display = serializers.CharField(source='get_verify_type_display', read_only=True)
    
    class Meta:
        model = AttendanceRecord
        fields = '__all__'
        read_only_fields = ['created_at', 'processed_at']


class DailyAttendanceSerializer(serializers.ModelSerializer):
    """Serializer for DailyAttendance"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    user_employee_id = serializers.CharField(source='user.employee_id', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = DailyAttendance
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'approved_at']


class LeaveRequestSerializer(serializers.ModelSerializer):
    """Serializer for LeaveRequest"""
    user_name = serializers.CharField(source='user.username', read_only=True)
    leave_type_display = serializers.CharField(source='get_leave_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    reviewed_by_name = serializers.CharField(source='reviewed_by.username', read_only=True, allow_null=True)
    
    class Meta:
        model = LeaveRequest
        fields = '__all__'
        read_only_fields = ['created_at', 'updated_at', 'reviewed_at', 'reviewed_by']
