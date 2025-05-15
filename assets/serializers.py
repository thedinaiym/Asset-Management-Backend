from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Asset
from rest_framework import generics, viewsets, filters

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)
    role = serializers.ChoiceField(choices=[('user','User'),('admin','Admin')], write_only=True)

    class Meta:
        model = User
        fields = ['id','username','email','password','role']

    def create(self, validated_data):
        role = validated_data.pop('role')
        user = User.objects.create_user(**validated_data)
        if role == 'admin':
            user.is_staff = True
            user.is_superuser = True
            user.save()
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','email']

class AssetSerializer(serializers.ModelSerializer):
    photo = serializers.ImageField(use_url=True, required=False)
    owner = serializers.SlugRelatedField(slug_field='username', read_only=True)
    pending_user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    linked_asset = serializers.PrimaryKeyRelatedField(read_only=True)

    class Meta:
        model = Asset
        fields = [
            'id','asset_type','title','description','photo',
            'owner','pending_user','status','created_at',
            'action_type','linked_asset','rating_before','rating_after'
        ]

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    def validate_old_password(self, value):
        user = self.context['request'].user
        if not user.check_password(value):
            raise serializers.ValidationError("Неверный текущий пароль")
        return value