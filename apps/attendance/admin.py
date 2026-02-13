"""
Admin interface for Attendance Management
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import AttendanceRecord, DailyAttendance, LeaveRequest


@admin.register(AttendanceRecord)
class AttendanceRecordAdmin(admin.ModelAdmin):
    """Attendance Record Admin"""
    list_display = ('user', 'device', 'timestamp', 'verify_type', 
                    'verify_code_display', 'is_processed')
    list_filter = ('verify_type', 'verify_code', 'is_processed', 'timestamp', 'device')
    search_fields = ('user__username', 'user__employee_id', 'device__name')
    readonly_fields = ('created_at', 'processed_at')
    date_hierarchy = 'timestamp'
    
    def verify_code_display(self, obj):
        """Display verify code meaning"""
        codes = {0: 'Check In', 1: 'Check Out', 2: 'Break Out', 3: 'Break In', 4: 'Overtime In', 5: 'Overtime Out'}
        return codes.get(obj.verify_code, f'Code {obj.verify_code}')
    verify_code_display.short_description = 'Action'


@admin.register(DailyAttendance)
class DailyAttendanceAdmin(admin.ModelAdmin):
    """Daily Attendance Admin"""
    list_display = ('user', 'date', 'check_in', 'check_out', 'status_badge', 
                    'work_hours', 'late_minutes', 'is_approved')
    list_filter = ('status', 'is_approved', 'date')
    search_fields = ('user__username', 'user__employee_id')
    readonly_fields = ('created_at', 'updated_at', 'approved_at')
    date_hierarchy = 'date'
    actions = ['approve_attendance', 'calculate_hours']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('user', 'date', 'status')
        }),
        ('Time Records', {
            'fields': ('check_in', 'check_out', 'work_hours', 'overtime_hours')
        }),
        ('Performance Indicators', {
            'fields': ('late_minutes', 'early_leave_minutes')
        }),
        ('Approval', {
            'fields': ('is_approved', 'approved_by', 'approved_at', 'notes')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'present': '#28a745',
            'late': '#ffc107',
            'absent': '#dc3545',
            'leave': '#17a2b8',
            'holiday': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def approve_attendance(self, request, queryset):
        """Approve selected attendance records"""
        from django.utils import timezone
        count = queryset.update(
            is_approved=True,
            approved_by=request.user,
            approved_at=timezone.now()
        )
        self.message_user(request, f'{count} attendance records approved.')
    approve_attendance.short_description = 'Approve selected attendance'
    
    def calculate_hours(self, request, queryset):
        """Calculate work hours for selected records"""
        count = 0
        for record in queryset:
            record.calculate_work_hours()
            count += 1
        self.message_user(request, f'Work hours calculated for {count} records.')
    calculate_hours.short_description = 'Calculate work hours'


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    """Leave Request Admin"""
    list_display = ('user', 'leave_type', 'start_date', 'end_date', 
                    'days_count', 'status_badge', 'reviewed_by')
    list_filter = ('status', 'leave_type', 'start_date')
    search_fields = ('user__username', 'user__employee_id', 'reason')
    readonly_fields = ('created_at', 'updated_at', 'reviewed_at')
    date_hierarchy = 'start_date'
    actions = ['approve_requests', 'reject_requests']
    
    fieldsets = (
        ('Employee Information', {
            'fields': ('user',)
        }),
        ('Leave Details', {
            'fields': ('leave_type', 'start_date', 'end_date', 'days_count', 
                      'reason', 'attachment')
        }),
        ('Review', {
            'fields': ('status', 'reviewed_by', 'review_notes', 'reviewed_at')
        }),
        ('System', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545',
            'cancelled': '#6c757d',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def approve_requests(self, request, queryset):
        """Approve selected leave requests"""
        count = 0
        for leave in queryset.filter(status='pending'):
            leave.approve(request.user)
            count += 1
        self.message_user(request, f'{count} leave requests approved.')
    approve_requests.short_description = 'Approve selected requests'
    
    def reject_requests(self, request, queryset):
        """Reject selected leave requests"""
        count = 0
        for leave in queryset.filter(status='pending'):
            leave.reject(request.user)
            count += 1
        self.message_user(request, f'{count} leave requests rejected.')
    reject_requests.short_description = 'Reject selected requests'
