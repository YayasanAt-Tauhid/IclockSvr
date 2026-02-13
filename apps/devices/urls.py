"""
URL routing for devices app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import DeviceViewSet, DeviceUserViewSet, DeviceLogViewSet

router = DefaultRouter()
router.register(r'', DeviceViewSet, basename='device')
router.register(r'users', DeviceUserViewSet, basename='device-user')
router.register(r'logs', DeviceLogViewSet, basename='device-log')

urlpatterns = [
    path('', include(router.urls)),
]
