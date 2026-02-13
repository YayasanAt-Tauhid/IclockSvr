"""
Attendance Tracking Models
"""
from django.db import models
from django.utils import timezone
from apps.accounts.models import User
from apps.devices.models import Device


class AttendanceRecord(models.Model):
    """Attendance record from devices"""
    VERIFY_TYPE_CHOICES = (
        (0, 'Password'),
        (1, 'Fingerprint'),
        (2, 'Card'),
        (3, 'Face'),
        (4, 'Iris'),
        (15, 'Palm'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='attendance_records')
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='attendance_records')
    timestamp = models.DateTimeField()
    verify_type = models.IntegerField(choices=VERIFY_TYPE_CHOICES, default=1)
    verify_code = models.IntegerField(default=0)  # 0=Check In, 1=Check Out, etc
    work_code = models.CharField(max_length=20, blank=True)
    temperature = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True)
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'attendance_records'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', 'timestamp']),
            models.Index(fields=['device', 'timestamp']),
            models.Index(fields=['is_processed']),
        ]
        verbose_name = 'Attendance Record'
        verbose_name_plural = 'Attendance Records'
    
    def __str__(self):
        return f"{self.user.username} - {self.timestamp}"
    
    def save(self, *args, **kwargs):
        """Auto-process on save"""
        if not self.is_processed:
            self.process_record()
        super().save(*args, **kwargs)
    
    def process_record(self):
        """Process attendance record to create daily summary"""
        from datetime import datetime, time
        
        date = self.timestamp.date()
        
        # Get or create daily attendance
        daily, created = DailyAttendance.objects.get_or_create(
            user=self.user,
            date=date,
            defaults={
                'check_in': self.timestamp if self.verify_code == 0 else None,
                'check_out': self.timestamp if self.verify_code == 1 else None,
            }
        )
        
        if not created:
            # Update existing record
            if self.verify_code == 0:  # Check in
                if not daily.check_in or self.timestamp < daily.check_in:
                    daily.check_in = self.timestamp
            elif self.verify_code == 1:  # Check out
                if not daily.check_out or self.timestamp > daily.check_out:
                    daily.check_out = self.timestamp
            
            daily.save()
        
        self.is_processed = True
        self.processed_at = timezone.now()


class DailyAttendance(models.Model):
    """Daily attendance summary"""
    STATUS_CHOICES = (
        ('present', 'Present'),
        ('late', 'Late'),
        ('absent', 'Absent'),
        ('leave', 'On Leave'),
        ('holiday', 'Holiday'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='daily_attendance')
    date = models.DateField()
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='absent')
    work_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    overtime_hours = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    late_minutes = models.IntegerField(default=0)
    early_leave_minutes = models.IntegerField(default=0)
    notes = models.TextField(blank=True)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                    blank=True, related_name='approved_attendance')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_attendance'
        unique_together = ['user', 'date']
        ordering = ['-date']
        indexes = [
            models.Index(fields=['user', 'date']),
            models.Index(fields=['date']),
            models.Index(fields=['status']),
        ]
        verbose_name = 'Daily Attendance'
        verbose_name_plural = 'Daily Attendance'
    
    def __str__(self):
        return f"{self.user.username} - {self.date}"
    
    def calculate_work_hours(self):
        """Calculate work hours"""
        if self.check_in and self.check_out:
            duration = self.check_out - self.check_in
            self.work_hours = round(duration.total_seconds() / 3600, 2)
            self.save()
    
    def calculate_late_minutes(self, standard_check_in_time='08:00'):
        """Calculate late minutes"""
        from datetime import datetime, time
        
        if self.check_in:
            standard_time = datetime.combine(self.date, 
                datetime.strptime(standard_check_in_time, '%H:%M').time())
            
            if self.check_in > standard_time:
                late_duration = self.check_in - standard_time
                self.late_minutes = int(late_duration.total_seconds() / 60)
                if self.late_minutes > 0:
                    self.status = 'late'
            else:
                self.status = 'present'
            
            self.save()


class LeaveRequest(models.Model):
    """Employee leave requests"""
    LEAVE_TYPE_CHOICES = (
        ('annual', 'Annual Leave'),
        ('sick', 'Sick Leave'),
        ('personal', 'Personal Leave'),
        ('emergency', 'Emergency Leave'),
        ('other', 'Other'),
    )
    
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('cancelled', 'Cancelled'),
    )
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    days_count = models.IntegerField(default=1)
    reason = models.TextField()
    attachment = models.FileField(upload_to='leave_attachments/', null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    reviewed_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                    blank=True, related_name='reviewed_leaves')
    review_notes = models.TextField(blank=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'leave_requests'
        ordering = ['-created_at']
        verbose_name = 'Leave Request'
        verbose_name_plural = 'Leave Requests'
    
    def __str__(self):
        return f"{self.user.username} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    def approve(self, reviewer):
        """Approve leave request"""
        self.status = 'approved'
        self.reviewed_by = reviewer
        self.reviewed_at = timezone.now()
        self.save()
        
        # Mark dates as leave in daily attendance
        from datetime import timedelta
        current_date = self.start_date
        while current_date <= self.end_date:
            DailyAttendance.objects.update_or_create(
                user=self.user,
                date=current_date,
                defaults={'status': 'leave'}
            )
            current_date += timedelta(days=1)
    
    def reject(self, reviewer, notes=''):
        """Reject leave request"""
        self.status = 'rejected'
        self.reviewed_by = reviewer
        self.review_notes = notes
        self.reviewed_at = timezone.now()
        self.save()
