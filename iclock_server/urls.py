"""
iClock Server URL Configuration
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from apps.devices.iclock_views import iclock_cdata, iclock_getrequest, iclock_devicecmd
from apps.devices.iclock_data_api import department_api, employee_api, transaction_api
from django.views.generic import TemplateView

urlpatterns = [
    # Admin panel
    path('admin/', admin.site.urls),

    # API endpoints
    path('api/auth/', include('apps.accounts.urls')),
    path('api/devices/', include('apps.devices.urls')),
    path('api/attendance/', include('apps.attendance.urls')),

    # Frontend
    # iClock Protocol endpoints (for fingerprint devices)
    path('iclock/cdata', iclock_cdata, name='iclock-cdata'),
    path('iclock/getrequest', iclock_getrequest, name='iclock-getrequest'),
    path('iclock/devicecmd', iclock_devicecmd, name='iclock-devicecmd'),
    path('iclock/data/department/', department_api, name='iclock-department'),
    path('iclock/data/employee/', employee_api, name='iclock-employee'),
    path('iclock/data/transaction/', transaction_api, name='iclock-transaction'),

    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('dashboard/', TemplateView.as_view(template_name='dashboard.html'), name='dashboard'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Admin site customization
admin.site.site_header = "iClock Server Administration"
admin.site.site_title = "iClock Admin Portal"
admin.site.index_title = "Welcome to iClock Server Admin Panel"
