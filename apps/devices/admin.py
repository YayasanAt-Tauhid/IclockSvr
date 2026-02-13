"""
Admin interface for Device Management
"""
from django.contrib import admin
from django.utils.html import format_html
from .models import Device, DeviceUser, DeviceLog


@admin.register(Device)
class DeviceAdmin(admin.ModelAdmin):
    """Device Admin"""
    list_display = ('name', 'serial_number', 'ip_address', 'location', 
                    'status_badge', 'is_active_badge', 'last_online')
    list_filter = ('status', 'is_active', 'device_type', 'created_at')
    search_fields = ('name', 'serial_number', 'ip_address', 'location')
    readonly_fields = ('created_at', 'updated_at', 'last_online')
    
    fieldsets = (
        ('Device Information', {
            'fields': ('serial_number', 'name', 'device_type', 'firmware_version')
        }),
        ('Network Configuration', {
            'fields': ('ip_address', 'port')
        }),
        ('Location & Status', {
            'fields': ('location', 'status', 'is_active', 'last_online')
        }),
        ('Additional Information', {
            'fields': ('notes', 'created_by', 'created_at', 'updated_at')
        }),
    )
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            'online': '#28a745',
            'offline': '#dc3545',
            'maintenance': '#ffc107',
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def is_active_badge(self, obj):
        """Display active status"""
        if obj.is_active:
            return format_html('<span style="color: green;">●</span> Active')
        return format_html('<span style="color: red;">●</span> Inactive')
    is_active_badge.short_description = 'Active'


@admin.register(DeviceUser)
class DeviceUserAdmin(admin.ModelAdmin):
    """Device User Admin"""
    list_display = ('user', 'device', 'device_user_id', 'is_synced', 'synced_at')
    list_filter = ('is_synced', 'device', 'created_at')
    search_fields = ('user__username', 'device__name', 'device_user_id', 'card_number')
    readonly_fields = ('created_at', 'updated_at', 'synced_at')


@admin.register(DeviceLog)
class DeviceLogAdmin(admin.ModelAdmin):
    """Device Log Admin"""
    list_display = ('device', 'log_type', 'message_preview', 'timestamp')
    list_filter = ('log_type', 'device', 'timestamp')
    search_fields = ('device__name', 'log_type', 'message')
    readonly_fields = ('timestamp',)
    
    def message_preview(self, obj):
        """Show preview of message"""
        return obj.message[:100] + '...' if len(obj.message) > 100 else obj.message
    message_preview.short_description = 'Message'
