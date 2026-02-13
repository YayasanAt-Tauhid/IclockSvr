#!/usr/bin/env python3
"""
Script to add download_attlog and move_employee features
"""

def add_download_attlog_feature():
    """Add download_attlog feature to attendance views"""
    
    file_path = 'apps/attendance/views.py'
    
    # Read current content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if feature already exists
    if 'download_attlog' in content:
        print("✅ download_attlog feature already exists")
        return False
    
    # Add HttpResponse import if not exists
    if 'from django.http import HttpResponse' not in content:
        content = content.replace(
            'from django.db.models import Q',
            'from django.db.models import Q\nfrom django.http import HttpResponse'
        )
    
    # Find position to insert (after bulk_create method)
    insert_marker = '        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)'
    
    new_method = '''
    
    @action(detail=False, methods=['get'])
    def download_attlog(self, request):
        """
        Download attendance log in x_attlog.dat format (ZKTeco format)
        Query params: start_date, end_date, device_id
        """
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can download attendance logs.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Get query parameters
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        device_id = request.query_params.get('device_id')
        
        queryset = self.get_queryset()
        
        # Apply filters
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        if device_id:
            queryset = queryset.filter(device_id=device_id)
        
        # Generate .dat file content
        # Format: PIN\\tDateTime\\tStatus\\tVerifyType\\tWorkCode
        lines = []
        for record in queryset:
            pin = record.user.employee_id or record.user.username
            datetime_str = record.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            status_code = record.verify_code
            verify_type = record.verify_type
            work_code = record.work_code or '0'
            
            line = f"{pin}\\t{datetime_str}\\t{status_code}\\t{verify_type}\\t{work_code}"
            lines.append(line)
        
        # Create response
        content = '\\n'.join(lines)
        response = HttpResponse(content, content_type='text/plain')
        
        # Set filename
        filename = f"x_attlog_{timezone.now().strftime('%Y%m%d_%H%M%S')}.dat"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'
        
        return response'''
    
    # Insert new method
    content = content.replace(insert_marker, insert_marker + new_method)
    
    # Write back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Added download_attlog feature to attendance/views.py")
    return True


def add_move_employee_feature():
    """Add move_employee feature to devices views"""
    
    file_path = 'apps/devices/views.py'
    
    # Read current content
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Check if feature already exists
    if 'move_employee' in content:
        print("✅ move_employee feature already exists")
        return False
    
    # Add imports if not exists
    if 'from django.db import transaction' not in content:
        content = content.replace(
            'from rest_framework import viewsets, filters',
            'from rest_framework import viewsets, filters, status\nfrom django.db import transaction'
        )
    elif ', status' not in content:
        content = content.replace(
            'from rest_framework import viewsets, filters',
            'from rest_framework import viewsets, filters, status'
        )
    
    # Find position to insert (after sync method in DeviceUserViewSet)
    insert_marker = '        return Response({\'status\': \'synced\', \'synced_at\': device_user.synced_at})'
    
    new_method = '''
    
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
            return Response({'error': f'Failed: {str(e)}'}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)'''
    
    # Insert new method
    content = content.replace(insert_marker, insert_marker + new_method)
    
    # Write back
    with open(file_path, 'w') as f:
        f.write(content)
    
    print("✅ Added move_employee feature to devices/views.py")
    return True


if __name__ == '__main__':
    print("🚀 Adding new features to IclockSvr...\n")
    
    changed = False
    
    if add_download_attlog_feature():
        changed = True
    
    if add_move_employee_feature():
        changed = True
    
    if changed:
        print("\n✅ All features added successfully!")
        print("\n📝 Next steps:")
        print("1. Restart service: sudo systemctl restart iclock")
        print("2. Commit changes: git add . && git commit -m 'Add download attlog and move employee features'")
        print("3. Push to GitHub: git push")
    else:
        print("\n✅ All features already exist!")
