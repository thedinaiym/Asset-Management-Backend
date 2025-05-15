from django.contrib.auth.models import User
from django.urls import reverse
from django.http import HttpResponse
from rest_framework import viewsets, generics, status, filters
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework.decorators import action
import qrcode, io
from reportlab.pdfgen import canvas

from .models import Asset
from .serializers import (
    AssetSerializer,
    RegisterSerializer,
    UserSerializer,
    ChangePasswordSerializer
)


class RegisterView(generics.CreateAPIView):
    """
    Регистрация нового пользователя
    """
    queryset = User.objects.all()
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer


class UsersWithAssetsView(generics.ListAPIView):
    """
    Список пользователей, у которых есть хотя бы один объект
    """
    queryset = User.objects.filter(assets__isnull=False).distinct()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]


class AssetViewSet(viewsets.ModelViewSet):
    """
    CRUD и кастомные операции для Asset
    """
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [filters.OrderingFilter, filters.SearchFilter]
    search_fields = ['owner__username', 'pending_user__username']

    def get_serializer_context(self):
        # Пробрасываем request в сериализатор для build_absolute_uri
        return {'request': self.request}

    def get_queryset(self):
        user = self.request.user
        # Админ видит все, остальные только свои
        qs = Asset.objects.all() if user.is_staff else Asset.objects.filter(owner=user)
        owner_id = self.request.query_params.get('owner')
        if owner_id:
            qs = qs.filter(owner__id=owner_id)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        if user.is_staff:
            # Админ создаёт сразу свободный
            serializer.save(status='free')
        else:
            # Обычный пользователь создаёт в pending
            serializer.save(pending_user=user, status='pending')

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='assign')
    def assign(self, request, pk=None):
        """
        Админ назначает asset пользователю, который его запросил
        """
        asset = self.get_object()
        if not request.user.is_staff:
            return Response({'detail': 'Требуются права администратора'}, status=status.HTTP_403_FORBIDDEN)
        asset.status = 'assigned'
        asset.owner = asset.pending_user
        asset.pending_user = None
        asset.save()
        return Response(self.get_serializer(asset).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='free')
    def free(self, request, pk=None):
        """
        Админ освобождает asset (возвращает в free)
        """
        asset = self.get_object()
        if not request.user.is_staff:
            return Response({'detail': 'Требуются права администратора'}, status=status.HTTP_403_FORBIDDEN)
        asset.status = 'free'
        asset.owner = None
        asset.pending_user = None
        asset.save()
        return Response(self.get_serializer(asset).data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated], url_path='qr', url_name='asset-qr')
    def qr(self, request, pk=None):
        """
        Генерация QR-кода в PNG для assigned asset
        """
        asset = self.get_object()
        if asset.status != 'assigned':
            return Response({'detail': 'QR доступен только при статусе assigned'}, status=status.HTTP_404_NOT_FOUND)
        url = request.build_absolute_uri(reverse('asset-detail-web', args=[asset.id]))
        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return HttpResponse(buf, content_type='image/png')

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated], url_path='qr-pdf')
    def qr_pdf(self, request, pk=None):
        """
        Генерация PDF с QR-кодом для assigned asset
        """
        asset = self.get_object()
        if asset.status != 'assigned':
            return Response({'detail': 'PDF QR доступен только при статусе assigned'}, status=status.HTTP_404_NOT_FOUND)
        url = request.build_absolute_uri(reverse('asset-detail-web', args=[asset.id]))
        # PNG в буфер
        img = qrcode.make(url)
        buf_img = io.BytesIO()
        img.save(buf_img, format='PNG')
        buf_img.seek(0)
        # PDF
        buf_pdf = io.BytesIO()
        p = canvas.Canvas(buf_pdf)
        p.drawInlineImage(buf_img, 100, 500, 200, 200)
        p.showPage()
        p.save()
        buf_pdf.seek(0)
        return HttpResponse(buf_pdf, content_type='application/pdf')


class ProfileView(APIView):
    """
    Просмотр данных текущего пользователя
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response(UserSerializer(request.user).data)


class ChangePasswordView(APIView):
    """
    Смена пароля для текущего пользователя
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)