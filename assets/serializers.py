from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Asset

class AssetSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    pending_username = serializers.CharField(source='pending_user.username', read_only=True)

    class Meta:
        model = Asset
        fields = [
            'id', 'title', 'description', 'asset_type', 'photo',
            'status',
            'owner', 'owner_username',
            'pending_user', 'pending_username',
            'created_at',
        ]
        read_only_fields = ['created_at', 'owner_username', 'pending_username']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[('user','User'),('admin','Admin')], write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'role']

    def create(self, validated_data):
        role = validated_data.pop('role')
        user = User.objects.create_user(**validated_data)
        if role == 'admin':
            user.is_staff = True
            user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email']
