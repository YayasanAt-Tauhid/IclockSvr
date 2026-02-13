"""
iClock Data REST API
Provides REST endpoints for data synchronization
"""
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework import status
from apps.accounts.models import User
from apps.devices.models import Device
from apps.attendance.models import AttendanceRecord
from django.http import JsonResponse


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@permission_classes([AllowAny])
@permission_classes([AllowAny])
@permission_classes([AllowAny])
def department_api(request):
    """
    Department API
    GET: List all departments
    POST: Create/Update department
    """
    if request.method == 'GET':
        # Return departments (for now, empty or from User groups)
        departments = []
        return Response({
            'code': 0,
            'msg': 'success',
            'data': departments
        })
    
    elif request.method == 'POST':
        # Create/Update department
        return Response({
            'code': 0,
            'msg': 'Department saved'
        })


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@permission_classes([AllowAny])
@permission_classes([AllowAny])
@permission_classes([AllowAny])
def employee_api(request):
    """
    Employee API
    GET: List all employees
    POST: Create/Update employee
    """
    if request.method == 'GET':
        # Return all users as employees
        users = User.objects.filter(is_active=True)
        employees = []
        
        for user in users:
            employees.append({
                'id': user.id,
                'emp_code': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'email': user.email,
                'department': '',
                'position': '',
                'hire_date': user.date_joined.strftime('%Y-%m-%d') if user.date_joined else '',
            })
        
        return Response({
            'code': 0,
            'msg': 'success',
            'count': len(employees),
            'data': employees
        })
    
    elif request.method == 'POST':
        # Create/Update employee
        data = request.data
        emp_code = data.get('emp_code')
        
        if not emp_code:
            return Response({
                'code': 1,
                'msg': 'emp_code is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user, created = User.objects.get_or_create(
            username=emp_code,
            defaults={
                'first_name': data.get('first_name', ''),
                'last_name': data.get('last_name', ''),
                'email': data.get('email', f'{emp_code}@local'),
            }
        )
        
        return Response({
            'code': 0,
            'msg': 'Employee saved',
            'data': {'id': user.id, 'emp_code': user.username}
        })


@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
@permission_classes([AllowAny])
@permission_classes([AllowAny])
@permission_classes([AllowAny])
def transaction_api(request):
    """
    Transaction API (Attendance Records)
    GET: List attendance transactions with filters
    POST: Create transaction (usually from device)
    """
    if request.method == 'GET':
        # Get query parameters
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
        emp_code = request.GET.get('emp_code')
        device_sn = request.GET.get('device_sn')
        
        # Filter attendance records
        records = AttendanceRecord.objects.all()
        
        if start_date:
            records = records.filter(timestamp__gte=start_date)
        if end_date:
            records = records.filter(timestamp__lte=end_date)
        if emp_code:
            records = records.filter(user__username=emp_code)
        if device_sn:
            records = records.filter(device__serial_number=device_sn)
        
        # Limit to latest 1000 records
        records = records.order_by('-timestamp')[:1000]
        
        transactions = []
        for rec in records:
            transactions.append({
                'id': rec.id,
                'emp_code': rec.user.username,
                'device_sn': rec.device.serial_number,
                'timestamp': rec.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
                'verify_type': getattr(rec, 'verify_type', '1'),
                'status': 'processed' if rec.is_processed else 'pending'
            })
        
        return Response({
            'code': 0,
            'msg': 'success',
            'count': len(transactions),
            'data': transactions
        })
    
    elif request.method == 'POST':
        # Create transaction
        data = request.data
        emp_code = data.get('emp_code')
        device_sn = data.get('device_sn')
        timestamp = data.get('timestamp')
        
        if not all([emp_code, device_sn, timestamp]):
            return Response({
                'code': 1,
                'msg': 'emp_code, device_sn, and timestamp are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create user and device
        user, _ = User.objects.get_or_create(
            username=emp_code,
            defaults={'email': f'{emp_code}@local'}
        )
        
        device, _ = Device.objects.get_or_create(
            serial_number=device_sn,
            defaults={
                'name': f'Device {device_sn}',
                'ip_address': '0.0.0.0',
                'location': ''
            }
        )
        
        # Create attendance record
        from django.utils import timezone
        from datetime import datetime
        
        dt = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
        dt_aware = timezone.make_aware(dt)
        
        record, created = AttendanceRecord.objects.get_or_create(
            user=user,
            device=device,
            timestamp=dt_aware,
            defaults={
                'verify_type': data.get('verify_type', '1'),
                'is_processed': False
            }
        )
        
        return Response({
            'code': 0,
            'msg': 'Transaction created' if created else 'Transaction already exists',
            'data': {'id': record.id}
        })
