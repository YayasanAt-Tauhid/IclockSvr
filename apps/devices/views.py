"""
API Views for Device Management
"""
from rest_framework import viewsets, filters, status
from django.db import transaction
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
    
    @action(detail=False, methods=['post'])
    def move_employee(self, request):
        """
        Move employee from one device to another
        Body params: 
        - user_id: ID of the user to move
        - source_device_id: ID of the source device
        - target_device_id: ID of the target device
        - copy_templates: boolean (default: true) - copy biometric templates
        """
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can move employees between devices.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user_id = request.data.get('user_id')
        source_device_id = request.data.get('source_device_id')
        target_device_id = request.data.get('target_device_id')
        copy_templates = request.data.get('copy_templates', True)
        
        # Validate input
        if not all([user_id, source_device_id, target_device_id]):
            return Response(
                {'error': 'user_id, source_device_id, and target_device_id are required.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if source_device_id == target_device_id:
            return Response(
                {'error': 'Source and target device cannot be the same.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            # Get devices
            source_device = Device.objects.get(id=source_device_id)
            target_device = Device.objects.get(id=target_device_id)
            
            # Get source device user
            source_device_user = DeviceUser.objects.get(
                device=source_device,
                user_id=user_id
            )
            
            # Use transaction to ensure data consistency
            with transaction.atomic():
                # Check if user already exists in target device
                target_device_user, created = DeviceUser.objects.get_or_create(
                    device=target_device,
                    user_id=user_id,
                    defaults={
                        'device_user_id': source_device_user.device_user_id,
                        'privilege': source_device_user.privilege,
                        'password': source_device_user.password,
                        'card_number': source_device_user.card_number,
                    }
                )
                
                # Copy biometric templates if requested
                if copy_templates:
                    target_device_user.fingerprint_templates = source_device_user.fingerprint_templates
                    target_device_user.face_templates = source_device_user.face_templates
                    target_device_user.is_synced = False
                    target_device_user.save()
                
                # Log the move operation
                DeviceLog.objects.create(
                    device=source_device,
                    log_type='employee_moved',
                    message=f'Employee {source_device_user.user.username} moved to {target_device.name}',
                    details={
                        'user_id': user_id,
                        'target_device': target_device.name,
                        'moved_by': request.user.username,
                    }
                )
                
                DeviceLog.objects.create(
                    device=target_device,
                    log_type='employee_added',
                    message=f'Employee {source_device_user.user.username} moved from {source_device.name}',
                    details={
                        'user_id': user_id,
                        'source_device': source_device.name,
                        'moved_by': request.user.username,
                    }
                )
            
            return Response({
                'message': f'Employee successfully moved from {source_device.name} to {target_device.name}',
                'source_device': {'id': source_device.id, 'name': source_device.name},
                'target_device': {'id': target_device.id, 'name': target_device.name},
                'user': {
                    'id': source_device_user.user.id,
                    'username': source_device_user.user.username,
                },
                'templates_copied': copy_templates,
            }, status=status.HTTP_200_OK)
            
        except Device.DoesNotExist:
            return Response({'error': 'Device not found'}, status=status.HTTP_404_NOT_FOUND)
        except DeviceUser.DoesNotExist:
            return Response({'error': 'Employee not found in source device'}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({'error': f'Failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class DeviceLogViewSet(viewsets.ReadOnlyModelViewSet):
    """API endpoint for device logs (read-only)"""
    queryset = DeviceLog.objects.all()
    serializer_class = DeviceLogSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['device', 'log_type']
    search_fields = ['message', 'log_type']
    ordering_fields = ['timestamp']
