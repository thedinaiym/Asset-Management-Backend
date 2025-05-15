from rest_framework import serializers
from django.urls import reverse
from .models import Asset

class AssetSerializer(serializers.ModelSerializer):
    photo_url = serializers.SerializerMethodField()
    qr_url    = serializers.SerializerMethodField()

    class Meta:
        model = Asset
        fields = [
            'id','asset_type','title','description',
            'photo_url','status',
            'owner_username','created_at','qr_url',
        ]

    def get_photo_url(self, obj):
        if not obj.photo:
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(obj.photo.url)

    def get_qr_url(self, obj):
        if obj.status != 'assigned':
            return None
        request = self.context.get('request')
        return request.build_absolute_uri(
            reverse('asset-qr', args=[obj.id])
        )
