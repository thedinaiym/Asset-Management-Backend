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
    owner_username        = serializers.CharField(source='owner.username', read_only=True)
    pending_user_username = serializers.CharField(source='pending_user.username', read_only=True)
    photo_url             = serializers.SerializerMethodField()
    qr_url                = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = [
            'id','asset_type','title','description',
            'photo_url','status',
            'owner_username','pending_user_username',
            'created_at','qr_url',
        ]
        read_only_fields = ['created_at','qr_url']

    def get_photo_url(self, obj):
        if obj.photo:
            return self.context['request'].build_absolute_uri(obj.photo.url)
        return None

    def get_qr_url(self, obj):
        if obj.status == 'assigned':
            return self.context['request'].build_absolute_uri(
                reverse('asset-qr', args=[obj.id])
            )
        return None

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)
