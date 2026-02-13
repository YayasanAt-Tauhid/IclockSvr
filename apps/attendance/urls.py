"""
URL routing for attendance app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AttendanceRecordViewSet, DailyAttendanceViewSet, LeaveRequestViewSet

router = DefaultRouter()
router.register(r'records', AttendanceRecordViewSet, basename='attendance-record')
router.register(r'daily', DailyAttendanceViewSet, basename='daily-attendance')
router.register(r'leaves', LeaveRequestViewSet, basename='leave-request')

urlpatterns = [
    path('', include(router.urls)),
]
