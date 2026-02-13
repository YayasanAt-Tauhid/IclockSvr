"""
Admin interface for User management
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.html import format_html
from .models import User, UserProfile


class UserProfileInline(admin.StackedInline):
    """Inline admin for UserProfile"""
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Information'
    fields = ('address', 'city', 'state', 'postal_code', 'country', 
              'date_of_birth', 'gender', 'emergency_contact', 'emergency_phone', 'notes')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User Admin"""
    inlines = (UserProfileInline,)
    
    list_display = ('username', 'email', 'employee_id', 'role_badge', 'department', 
                    'is_active_badge', 'created_at')
    list_filter = ('role', 'is_active', 'is_staff', 'department', 'created_at')
    search_fields = ('username', 'email', 'employee_id', 'first_name', 'last_name', 'department')
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'email', 'phone', 'photo')}),
        ('Employee Info', {'fields': ('employee_id', 'department', 'role')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'employee_id', 'role', 'password1', 'password2'),
        }),
    )
    
    def role_badge(self, obj):
        """Display role with colored badge"""
        colors = {
            'admin': '#dc3545',
            'manager': '#ffc107',
            'user': '#28a745',
            'device': '#17a2b8',
        }
        color = colors.get(obj.role, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; '
            'border-radius: 3px; font-size: 11px;">{}</span>',
            color, obj.get_role_display()
        )
    role_badge.short_description = 'Role'
    
    def is_active_badge(self, obj):
        """Display active status with badge"""
        if obj.is_active:
            return format_html(
                '<span style="color: green;">●</span> Active'
            )
        return format_html(
            '<span style="color: red;">●</span> Inactive'
        )
    is_active_badge.short_description = 'Status'
    
    def save_model(self, request, obj, form, change):
        """Create profile when user is created"""
        super().save_model(request, obj, form, change)
        if not change:  # New user
            UserProfile.objects.get_or_create(user=obj)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """User Profile Admin"""
    list_display = ('user', 'city', 'country', 'date_of_birth', 'gender')
    search_fields = ('user__username', 'user__email', 'city', 'country')
    list_filter = ('country', 'gender')
