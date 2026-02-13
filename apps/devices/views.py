"""
API Views for Device Management
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import Device, DeviceUser, DeviceLog
from .serializers import DeviceSerializer, DeviceUserSerializer, DeviceLogSerializer


class DeviceViewSet(viewsets.ModelViewSet):
    """API endpoint for device management"""
    queryset = Device.objects.all()
    serializer_class = DeviceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['status', 'is_active', 'device_type']
    search_fields = ['name', 'serial_number', 'ip_address', 'location']
    ordering_fields = ['created_at', 'name', 'last_online']
    
    def perform_create(self, serializer):
        """Save device with creator"""
        serializer.save(created_by=self.request.user)
    
    @action(detail=True, methods=['post'])
    def ping(self, request, pk=None):
        """Ping device to check online status"""
        device = self.get_object()
        device.last_online = timezone.now()
        device.status = 'online'
        device.save()
        
        # Log the ping
        DeviceLog.objects.create(
            device=device,
            log_type='ping',
            message='Device pinged successfully'
        )
        
        return Response({'status': 'online', 'last_online': device.last_online})
    
    @action(detail=True, methods=['get'])
    def logs(self, request, pk=None):
        """Get device logs"""
        device = self.get_object()
        logs = device.logs.all()[:50]
        serializer = DeviceLogSerializer(logs, many=True)
        return Response(serializer.data)


class DeviceUserViewSet(viewsets.ModelViewSet):
    """API endpoint for device user management"""
    queryset = DeviceUser.objects.all()
    serializer_class = DeviceUserSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['device', 'user', 'is_synced']
    search_fields = ['user__username', 'device__name', 'device_user_id']
    
    @action(detail=True, methods=['post'])
    def sync(self, request, pk=None):
        """Mark user as synced"""
        device_user = self.get_object()
        device_user.is_synced = True
        device_user.synced_at = timezone.now()
        device_user.save()
        
        return Response({'status': 'synced', 'synced_at': device_user.synced_at})


class DeviceLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for device logs (read-only)"""
    queryset = DeviceLog.objects.all()
    serializer_class = DeviceLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['device', 'log_type']
    search_fields = ['message', 'log_type']
    ordering_fields = ['timestamp']
