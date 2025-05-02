from rest_framework import viewsets, generics
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from django.contrib.auth.models import User
from .models import Asset
from .serializers import AssetSerializer, RegisterSerializer, UserSerializer
from rest_framework.decorators import action
from django.http import HttpResponse
import qrcode
import io
from django.urls import reverse

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer

class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
       
        if user.is_staff:
            return Asset.objects.all()
        else:
            return Asset.objects.filter(owner=user)

    def perform_create(self, serializer):
        serializer.save(owner=self.request.user)


    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def qr(self, request, pk=None):
        asset = self.get_object()
        # строим абсолютный URL к странице детали
        url = request.build_absolute_uri(
            reverse('asset-detail-web', args=[asset.id])
        )
        qr_img = qrcode.make(url)
        buffer = io.BytesIO()
        qr_img.save(buffer, format='PNG')
        buffer.seek(0)
        return HttpResponse(buffer, content_type='image/png')


class UserViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
