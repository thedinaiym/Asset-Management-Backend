# assets/serializers.py
from rest_framework import serializers
from django.contrib.auth.models import User
from django.urls import reverse
from .models import Asset


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'password')

    def create(self, validated_data):
        return User.objects.create_user(
            username=validated_data['username'],
            password=validated_data['password']
        )


class UserSerializer(serializers.ModelSerializer):
    assets_count = serializers.IntegerField(source='assets.count', read_only=True)

    class Meta:
        model = User
        fields = ('id', 'username', 'assets_count')


class AssetSerializer(serializers.ModelSerializer):
    owner_username = serializers.CharField(source='owner.username', read_only=True)
    photo_url      = serializers.SerializerMethodField()
    qr_url         = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = [
            'id', 'asset_type', 'title', 'description',
            'photo_url', 'status', 'owner', 'owner_username', 'pending_user',
            'created_at', 'qr_url'
        ]
        read_only_fields = ['owner', 'created_at', 'qr_url']

    def get_photo_url(self, obj):
        request = self.context.get('request')
        if obj.photo and request:
            return request.build_absolute_uri(obj.photo.url)
        return None

    def get_qr_url(self, obj):
        if obj.status != 'assigned':
            return None
        request = self.context.get('request')
        if not request:
            return None
        return request.build_absolute_uri(
            reverse('asset-qr', args=[obj.id])
        )


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
