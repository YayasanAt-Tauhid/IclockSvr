"""
API Views for Attendance Management
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from django.db.models import Q
from datetime import datetime, timedelta
from .models import AttendanceRecord, DailyAttendance, LeaveRequest
from .serializers import (
    AttendanceRecordSerializer,
    DailyAttendanceSerializer,
    LeaveRequestSerializer
)


class AttendanceRecordViewSet(viewsets.ModelViewSet):
    """API endpoint for attendance records"""
    queryset = AttendanceRecord.objects.all()
    serializer_class = AttendanceRecordSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user', 'device', 'verify_type', 'verify_code', 'is_processed']
    search_fields = ['user__username', 'user__employee_id', 'device__name']
    ordering_fields = ['timestamp', 'created_at']
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admins see all records
        if user.is_admin or user.is_superuser:
            return queryset
        
        # Regular users only see their own records
        return queryset.filter(user=user)
    
    @action(detail=False, methods=['post'])
    def bulk_create(self, request):
        """Bulk create attendance records (for device sync)"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can bulk create records.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = self.get_serializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class DailyAttendanceViewSet(viewsets.ModelViewSet):
    """API endpoint for daily attendance"""
    queryset = DailyAttendance.objects.all()
    serializer_class = DailyAttendanceSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user', 'date', 'status', 'is_approved']
    search_fields = ['user__username', 'user__employee_id']
    ordering_fields = ['date', 'created_at']
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admins see all records
        if user.is_admin or user.is_superuser:
            return queryset
        
        # Managers see their department
        if user.is_manager:
            return queryset.filter(
                Q(user__department=user.department) | Q(user=user)
            )
        
        # Regular users only see their own records
        return queryset.filter(user=user)
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve daily attendance"""
        if not (request.user.is_admin or request.user.is_manager):
            return Response(
                {'error': 'Only admins or managers can approve attendance.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        attendance = self.get_object()
        attendance.is_approved = True
        attendance.approved_by = request.user
        attendance.approved_at = timezone.now()
        attendance.save()
        
        return Response({
            'message': 'Attendance approved successfully.',
            'is_approved': True
        })
    
    @action(detail=False, methods=['get'])
    def report(self, request):
        """Generate attendance report"""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        user_id = request.query_params.get('user_id')
        
        queryset = self.get_queryset()
        
        if start_date:
            queryset = queryset.filter(date__gte=start_date)
        if end_date:
            queryset = queryset.filter(date__lte=end_date)
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Calculate statistics
        total_days = queryset.count()
        present_days = queryset.filter(status='present').count()
        late_days = queryset.filter(status='late').count()
        absent_days = queryset.filter(status='absent').count()
        leave_days = queryset.filter(status='leave').count()
        
        total_late_minutes = sum([a.late_minutes for a in queryset])
        total_work_hours = sum([float(a.work_hours) for a in queryset])
        
        return Response({
            'summary': {
                'total_days': total_days,
                'present_days': present_days,
                'late_days': late_days,
                'absent_days': absent_days,
                'leave_days': leave_days,
                'total_late_minutes': total_late_minutes,
                'total_work_hours': round(total_work_hours, 2)
            },
            'records': self.get_serializer(queryset, many=True).data
        })


class LeaveRequestViewSet(viewsets.ModelViewSet):
    """API endpoint for leave requests"""
    queryset = LeaveRequest.objects.all()
    serializer_class = LeaveRequestSerializer
    permission_classes = [IsAuthenticated]
    filterset_fields = ['user', 'leave_type', 'status']
    search_fields = ['user__username', 'user__employee_id', 'reason']
    ordering_fields = ['created_at', 'start_date']
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admins see all requests
        if user.is_admin or user.is_superuser:
            return queryset
        
        # Managers see their department
        if user.is_manager:
            return queryset.filter(
                Q(user__department=user.department) | Q(user=user)
            )
        
        # Regular users only see their own requests
        return queryset.filter(user=user)
    
    def perform_create(self, serializer):
        """Calculate days count when creating"""
        leave = serializer.save(user=self.request.user)
        days = (leave.end_date - leave.start_date).days + 1
        leave.days_count = days
        leave.save()
    
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve leave request"""
        if not (request.user.is_admin or request.user.is_manager):
            return Response(
                {'error': 'Only admins or managers can approve leave requests.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        leave = self.get_object()
        if leave.status != 'pending':
            return Response(
                {'error': 'Only pending requests can be approved.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        leave.approve(request.user)
        
        return Response({
            'message': 'Leave request approved successfully.',
            'status': 'approved'
        })
    
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject leave request"""
        if not (request.user.is_admin or request.user.is_manager):
            return Response(
                {'error': 'Only admins or managers can reject leave requests.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        leave = self.get_object()
        if leave.status != 'pending':
            return Response(
                {'error': 'Only pending requests can be rejected.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        notes = request.data.get('notes', '')
        leave.reject(request.user, notes)
        
        return Response({
            'message': 'Leave request rejected.',
            'status': 'rejected'
        })
