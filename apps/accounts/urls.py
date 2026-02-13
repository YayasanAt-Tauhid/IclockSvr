"""
URL routing for accounts app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import UserViewSet, login_view, logout_view, register_view

router = DefaultRouter()
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('', include(router.urls)),
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('register/', register_view, name='register'),
]
