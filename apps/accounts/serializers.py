"""
API Serializers for User Management
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """Serializer for UserProfile"""
    class Meta:
        model = UserProfile
        fields = ['address', 'city', 'state', 'postal_code', 'country',
                  'date_of_birth', 'gender', 'emergency_contact', 
                  'emergency_phone', 'notes']


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    profile = UserProfileSerializer(required=False)
    password = serializers.CharField(write_only=True, required=False)
    role_display = serializers.CharField(source='get_role_display', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name', 
                  'employee_id', 'department', 'phone', 'photo', 'role', 
                  'role_display', 'is_active', 'is_staff', 'created_at', 
                  'updated_at', 'profile', 'password']
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            'password': {'write_only': True}
        }
    
    def create(self, validated_data):
        """Create user with profile"""
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)
        
        user = User.objects.create(**validated_data)
        if password:
            user.set_password(password)
            user.save()
        
        # Create or update profile
        if profile_data:
            UserProfile.objects.update_or_create(user=user, defaults=profile_data)
        else:
            UserProfile.objects.get_or_create(user=user)
        
        return user
    
    def update(self, instance, validated_data):
        """Update user with profile"""
        profile_data = validated_data.pop('profile', None)
        password = validated_data.pop('password', None)
        
        # Update user fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        
        if password:
            instance.set_password(password)
        
        instance.save()
        
        # Update profile
        if profile_data:
            UserProfile.objects.update_or_create(
                user=instance, 
                defaults=profile_data
            )
        
        return instance


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validate and authenticate user"""
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            user = authenticate(username=username, password=password)
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError('User account is disabled.')
                data['user'] = user
            else:
                raise serializers.ValidationError('Unable to log in with provided credentials.')
        else:
            raise serializers.ValidationError('Must include "username" and "password".')
        
        return data


class ChangePasswordSerializer(serializers.Serializer):
    """Serializer for password change"""
    old_password = serializers.CharField(required=True, write_only=True)
    new_password = serializers.CharField(required=True, write_only=True)
    confirm_password = serializers.CharField(required=True, write_only=True)
    
    def validate(self, data):
        """Validate password change"""
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("New passwords don't match.")
        
        if len(data['new_password']) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        
        return data
