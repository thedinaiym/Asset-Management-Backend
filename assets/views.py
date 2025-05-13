# assets/views.py

from rest_framework import viewsets, generics, status, filters
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse
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


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class AssetViewSet(viewsets.ModelViewSet):
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['owner__username']

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
            serializer.save(owner=user, status='assigned')
        else:
            serializer.save(owner=None, status='pending', pending_user=user)

    def partial_update(self, request, *args, **kwargs):
        # Разрешаем редактировать только админам
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

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
        url = request.build_absolute_uri(reverse('asset-detail-web', args=[asset.id]))
        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return HttpResponse(buf, content_type='image/png')

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def qr_pdf(self, request, pk=None):
        asset = self.get_object()
        # Генерируем ссылку на веб-деталку
        url = request.build_absolute_uri(reverse('asset-detail-web', args=[asset.id]))
        # Сначала создаём PNG-изображение QR
        img = qrcode.make(url)
        buf_img = io.BytesIO()
        img.save(buf_img, format='PNG')
        buf_img.seek(0)
        # Затем создаём PDF и вставляем туда картинку
        buf_pdf = io.BytesIO()
        p = canvas.Canvas(buf_pdf)
        p.drawInlineImage(buf_img, 100, 500, 200, 200)  # координаты и размер можно настроить
        p.showPage()
        p.save()
        buf_pdf.seek(0)
        return HttpResponse(buf_pdf, content_type='application/pdf')


class ProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)
