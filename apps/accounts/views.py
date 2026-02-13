"""
API Views for User Management
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.contrib.auth import login, logout
from django.db.models import Q
from .models import User
from .serializers import (
    UserSerializer, LoginSerializer, 
    ChangePasswordSerializer
)


class IsAdminOrReadOnly(permissions.BasePermission):
    """
    Custom permission: Admin can do everything, others can only read
    """
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return request.user.is_authenticated
        return request.user.is_authenticated and (
            request.user.is_admin or request.user.is_superuser
        )


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint for user management
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_fields = ['role', 'is_active', 'department']
    search_fields = ['username', 'email', 'employee_id', 'first_name', 'last_name']
    ordering_fields = ['created_at', 'username', 'email']
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        user = self.request.user
        
        # Admins see all users
        if user.is_admin or user.is_superuser:
            return queryset
        
        # Managers see their department
        if user.is_manager:
            return queryset.filter(
                Q(department=user.department) | Q(id=user.id)
            )
        
        # Regular users only see themselves
        return queryset.filter(id=user.id)
    
    @action(detail=False, methods=['get'])
    def me(self, request):
        """Get current user information"""
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def change_password(self, request, pk=None):
        """Change user password"""
        user = self.get_object()
        
        # Only allow users to change their own password or admins to change any
        if user != request.user and not request.user.is_admin:
            return Response(
                {'error': 'You can only change your own password.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Check old password
            if not user.check_password(serializer.validated_data['old_password']):
                return Response(
                    {'error': 'Wrong password.'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            
            # Set new password
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            
            return Response({'message': 'Password updated successfully.'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def activate(self, request, pk=None):
        """Activate/deactivate user"""
        if not request.user.is_admin:
            return Response(
                {'error': 'Only admins can activate/deactivate users.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        user = self.get_object()
        user.is_active = not user.is_active
        user.save()
        
        return Response({
            'message': f'User {"activated" if user.is_active else "deactivated"} successfully.',
            'is_active': user.is_active
        })


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """
    User login endpoint
    """
    serializer = LoginSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.validated_data['user']
        
        # Login user
        login(request, user)
        
        # Get or create token
        token, created = Token.objects.get_or_create(user=user)
        
        # Return user data with token
        user_serializer = UserSerializer(user)
        return Response({
            'token': token.key,
            'user': user_serializer.data,
            'message': 'Login successful.'
        })
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """
    User logout endpoint
    """
    # Delete token
    try:
        request.user.auth_token.delete()
    except:
        pass
    
    # Logout user
    logout(request)
    
    return Response({'message': 'Logout successful.'})


@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register_view(request):
    """
    User registration endpoint
    """
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        token, created = Token.objects.get_or_create(user=user)
        
        return Response({
            'token': token.key,
            'user': serializer.data,
            'message': 'Registration successful.'
        }, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
