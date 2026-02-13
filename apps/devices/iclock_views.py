"""
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
iClock Protocol Views
Handle communication with fingerprint devices
"""
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from django.utils import timezone
from .models import Device, DeviceLog
from apps.attendance.models import AttendanceRecord
from apps.accounts.models import User
import logging

logger = logging.getLogger(__name__)


@csrf_exempt
@require_http_methods(["GET", "POST"])
def iclock_cdata(request):
    """
    Handle iClock protocol requests from fingerprint devices
    GET: Device registration and commands
    POST: Attendance data upload
    """
    sn = request.GET.get('SN', '')
    
    if not sn:
        return HttpResponse('ERROR: No SN provided', status=400)
    
    # Log request
    logger.info(f"iClock request from SN: {sn}, Method: {request.method}")
    
    if request.method == 'GET':
        return handle_device_registration(request, sn)
    elif request.method == 'POST':
        return handle_attendance_upload(request, sn)
    
    return HttpResponse('OK', status=200)


def handle_device_registration(request, sn):
    """
    Handle device registration and return commands
    Auto-create device if not exists
    """
    try:
        # Get or create device
        device, created = Device.objects.get_or_create(
            serial_number=sn,
            defaults={
                'name': f'Device {sn}',
                'ip_address': get_client_ip(request),
                'status': 'active',
                'last_online': timezone.now()
            }
        )
        
        if created:
            logger.info(f"New device auto-registered: {sn}")
            # Log device registration
            DeviceLog.objects.create(
                device=device,
                log_type='registration',
                message=f'Device auto-registered from IP: {get_client_ip(request)}'
            )
        else:
            # Update last activity
            device.last_online = timezone.now()
            device.save(update_fields=['last_online'])
        
        # Return commands (empty for now, can add later)
        # Format: OK or C:command
        return HttpResponse('OK', status=200)
        
    except Exception as e:
        logger.error(f"Error in device registration for {sn}: {str(e)}")
        return HttpResponse('ERROR', status=500)


def handle_attendance_upload(request, sn):
    """
    Handle attendance data upload from device
    Format: POST data contains attendance records
    """
    try:
        device = Device.objects.filter(serial_number=sn).first()
        
        if not device:
            # Auto-create if not exists
            device = Device.objects.create(
                serial_number=sn,
                name=f'Device {sn}',
                ip_address=get_client_ip(request),
                status='active',
                last_online=timezone.now()
            )
            logger.info(f"Device auto-created during upload: {sn}")
        
        # Parse attendance data from POST body
        body = request.body.decode('utf-8')
        logger.info(f"Attendance data from {sn}: {body[:200]}")
        
        # Parse iClock format data
        # Format typically: ATTLOG or similar
        lines = body.strip().split('\n')
        records_created = 0
        
        for line in lines:
            if line.startswith('ATTLOG'):
                # Parse format: ATTLOG\tpin\ttime\tstate\tverify
                # Example: ATTLOG\t1\t2024-01-15 08:30:00\t0\t1
                parts = line.split('\t')
                if len(parts) >= 3:
                    try:
                        user_id = parts[1]
                        timestamp_str = parts[2]
                        
                        # Find or create user
                        user, _ = User.objects.get_or_create(
                            username=f'emp_{user_id}',
                            defaults={'email': f'emp_{user_id}@local'}
                        )
                        
                        # Parse timestamp
                        from datetime import datetime
                        timestamp = datetime.strptime(timestamp_str, '%Y-%m-%d %H:%M:%S')
                        timestamp = timezone.make_aware(timestamp)
                        
                        # Create attendance record
                        AttendanceRecord.objects.get_or_create(
                            user=user,
                            device=device,
                            timestamp=timestamp,
                            defaults={
                                'verify_type': parts[4] if len(parts) > 4 else '1',
                                'is_processed': False
                            }
                        )
                        records_created += 1
                        
                    except Exception as e:
                        logger.error(f"Error parsing line: {line}, Error: {str(e)}")
                        continue
        
        logger.info(f"Created {records_created} attendance records from {sn}")
        
        # Update device last activity
        device.last_online = timezone.now()
        device.save(update_fields=['last_online'])
        
        # Return success
        return HttpResponse('OK', status=200)
        
    except Exception as e:
        logger.error(f"Error handling attendance upload from {sn}: {str(e)}")
        return HttpResponse('ERROR', status=500)


def get_client_ip(request):
    """Get client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


@csrf_exempt
def iclock_getrequest(request):
    """
    Handle getrequest from device
    Used for device configuration sync
    """
    sn = request.GET.get('SN', '')
    logger.info(f"getrequest from SN: {sn}")
    
    # Return empty or configuration commands
    return HttpResponse('OK', status=200)


@csrf_exempt  
def iclock_devicecmd(request):
    """
    Handle devicecmd - commands for device
    """
    sn = request.GET.get('SN', '')
    logger.info(f"devicecmd from SN: {sn}")
    
    # Return commands if any
    return HttpResponse('OK', status=200)
