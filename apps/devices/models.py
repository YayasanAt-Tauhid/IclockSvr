"""
Device Management Models
"""
from django.db import models
from apps.accounts.models import User


class Device(models.Model):
    """Attendance Device Model"""
    STATUS_CHOICES = (
        ('online', 'Online'),
        ('offline', 'Offline'),
        ('maintenance', 'Maintenance'),
    )
    
    serial_number = models.CharField(max_length=50, unique=True)
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=200)
    ip_address = models.GenericIPAddressField()
    port = models.IntegerField(default=4370)
    device_type = models.CharField(max_length=50, default='ZKTeco')
    firmware_version = models.CharField(max_length=50, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='offline')
    last_online = models.DateTimeField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='devices_created')
    
    class Meta:
        db_table = 'devices'
        ordering = ['-created_at']
        verbose_name = 'Device'
        verbose_name_plural = 'Devices'
    
    def __str__(self):
        return f"{self.name} ({self.serial_number})"


class DeviceUser(models.Model):
    """Users registered in attendance devices"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='device_users')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registered_devices')
    device_user_id = models.CharField(max_length=50)  # ID in the device
    fingerprint_templates = models.JSONField(default=list, blank=True)
    face_templates = models.JSONField(default=list, blank=True)
    card_number = models.CharField(max_length=50, blank=True)
    privilege = models.IntegerField(default=0)  # User privilege in device
    password = models.CharField(max_length=50, blank=True)
    is_synced = models.BooleanField(default=False)
    synced_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'device_users'
        unique_together = ['device', 'device_user_id']
        verbose_name = 'Device User'
        verbose_name_plural = 'Device Users'
    
    def __str__(self):
        return f"{self.user.username} on {self.device.name}"


class DeviceLog(models.Model):
    """Device system logs"""
    device = models.ForeignKey(Device, on_delete=models.CASCADE, related_name='logs')
    log_type = models.CharField(max_length=50)
    message = models.TextField()
    details = models.JSONField(default=dict, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'device_logs'
        ordering = ['-timestamp']
        verbose_name = 'Device Log'
        verbose_name_plural = 'Device Logs'
    
    def __str__(self):
        return f"{self.device.name} - {self.log_type} at {self.timestamp}"
