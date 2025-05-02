from rest_framework import viewsets, generics, status
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse
import qrcode
import io

from .models import Asset
from .serializers import (
    AssetSerializer,
    RegisterSerializer,
    UserSerializer,
    ChangePasswordSerializer
)

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
        return Asset.objects.filter(owner=user)

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff:
            serializer.save(owner=user, status='assigned')
        else:
            serializer.save(owner=None, status='pending', pending_user=user)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def approve(self, request, pk=None):
        asset = self.get_object()
        if not request.user.is_staff or asset.status != 'pending':
            return Response(status=status.HTTP_403_FORBIDDEN)
        asset.owner = asset.pending_user
        asset.status = 'assigned'
        asset.pending_user = None
        asset.save()
        return Response(self.get_serializer(asset).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def deny(self, request, pk=None):
        asset = self.get_object()
        if not request.user.is_staff or asset.status != 'pending':
            return Response(status=status.HTTP_403_FORBIDDEN)
        asset.status = 'free'
        asset.pending_user = None
        asset.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def qr(self, request, pk=None):
        asset = self.get_object()
        # динамический URL на Heroku
        url = request.build_absolute_uri(reverse('asset-detail-web', args=[asset.id]))
        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return HttpResponse(buf, content_type='image/png')

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        return Response(UserSerializer(request.user).data)

class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)