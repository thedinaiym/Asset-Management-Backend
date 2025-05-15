from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse
from rest_framework import viewsets, generics, status, filters
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
import qrcode
import io
from reportlab.pdfgen import canvas

from .models import Asset
from .serializers import (
    AssetSerializer,
    RegisterSerializer,
    UserSerializer,
    ChangePasswordSerializer
)

import qrcode, io
from reportlab.pdfgen import canvas

from .models import Asset
from .serializers import AssetSerializer, RegisterSerializer, UserSerializer, ChangePasswordSerializer



class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class UsersWithAssetsView(generics.ListAPIView):
    queryset = User.objects.filter(assets__isnull=False).distinct()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['owner__username']

    def get_serializer_context(self):
        return {'request': self.request}

    def get_queryset(self):
        user = self.request.user
        qs = Asset.objects.all() if user.is_staff else Asset.objects.filter(owner=user)
        owner_id = self.request.query_params.get('owner')
        if owner_id:
            qs = qs.filter(owner__id=owner_id)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff:
            serializer.save(status='free')  # админ создаёт сразу free
        else:
            serializer.save(pending_user=user, status='pending')

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='assign')
    def assign(self, request, pk=None):
        asset = self.get_object()
        asset.status = 'assigned'
        # назначаем владельцем того, кто запросил
        asset.owner = asset.pending_user
        asset.pending_user = None
        asset.save()
        return Response(self.get_serializer(asset).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='free')
    def free(self, request, pk=None):
        asset = self.get_object()
        asset.status = 'free'
        asset.owner = None
        asset.pending_user = None
        asset.save()
        return Response(self.get_serializer(asset).data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated], url_path='qr', url_name='asset-qr')
    def qr(self, request, pk=None):
        asset = self.get_object()
        # доступна только если assigned
        if asset.status != 'assigned':
            return Response(status=status.HTTP_404_NOT_FOUND)
        url = request.build_absolute_uri(
            reverse('asset-detail-web', args=[asset.id])
        )
        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format='PNG'); buf.seek(0)
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