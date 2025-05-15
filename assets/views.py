import io
import qrcode
from django.urls import reverse
from django.http import HttpResponse
from django.contrib.auth.models import User
from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.views import APIView
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.utils import ImageReader

from .models import Asset
from .serializers import AssetSerializer, RegisterSerializer, UserSerializer

class RegisterView(APIView):
    permission_classes = []  # open registration
    def post(self, request):
        ser = RegisterSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        user = ser.save()
        return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)

class AssetViewSet(viewsets.ModelViewSet):
    """
    CRUD + дополнительные действия:
      - PATCH            : смена любых полей (только для админа)
      - POST  approve    : одобрение pending-заявки (существовал раньше)
      - POST  deny       : отклонение pending-заявки
      - POST  return     : возврат assigned-asset пользователем
      - GET   qr         : PNG-QR
      - GET   qr_pdf     : PDF-QR
    """
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_staff:
            return Asset.objects.all()
        return Asset.objects.filter(models.Q(owner=user) | models.Q(pending_user=user))

    def perform_create(self, serializer):
        user = self.request.user
        # если админ — сразу assigned, иначе pending
        if user.is_staff:
            serializer.save(owner=user, status='assigned')
        else:
            serializer.save(pending_user=user, status='pending')

    def partial_update(self, request, *args, **kwargs):
        """
        PATCH /api/assets/<id>/ — доступно только для админа
        """
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        asset = self.get_object()
        if not request.user.is_staff or asset.status != 'pending':
            return Response(status=status.HTTP_403_FORBIDDEN)
        asset.owner = asset.pending_user
        asset.status = 'assigned'
        asset.pending_user = None
        asset.save()
        return Response(AssetSerializer(asset, context={'request': request}).data)

    @action(detail=True, methods=['post'])
    def deny(self, request, pk=None):
        asset = self.get_object()
        if not request.user.is_staff or asset.status != 'pending':
            return Response(status=status.HTTP_403_FORBIDDEN)
        asset.status = 'free'
        asset.pending_user = None
        asset.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def return_asset(self, request, pk=None):
        """
        Пользователь возвращает своё assigned-имущество
        POST /api/assets/<id>/return/
        """
        asset = self.get_object()
        if asset.status != 'assigned' or asset.owner != request.user:
            return Response(status=status.HTTP_403_FORBIDDEN)
        asset.status = 'free'
        asset.owner = None
        asset.save()
        return Response(AssetSerializer(asset, context={'request': request}).data)

    @action(detail=True, methods=['get'])
    def qr(self, request, pk=None):
        asset = self.get_object()
        url = request.build_absolute_uri(reverse('asset-detail-web', args=[asset.id]))
        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return HttpResponse(buf, content_type='image/png')

    @action(detail=True, methods=['get'])
    def qr_pdf(self, request, pk=None):
        asset = self.get_object()
        # строим URL для встраивания в QR
        url = request.build_absolute_uri(reverse('asset-detail-web', args=[asset.id]))
        qr_img = qrcode.make(url)
        # рисуем PDF
        packet = io.BytesIO()
        c = canvas.Canvas(packet, pagesize=letter)
        # конвертим PIL→ImageReader
        tmp = io.BytesIO()
        qr_img.save(tmp, format='PNG')
        tmp.seek(0)
        c.drawImage(ImageReader(tmp), 100, 500, width=200, height=200)
        c.showPage()
        c.save()
        packet.seek(0)
        response = HttpResponse(packet, content_type='application/pdf')
        response['Content-Disposition'] = f'attachment; filename="asset_{asset.id}_qr.pdf"'
        return response

class UsersWithAssetsView(APIView):
    """
    GET /api/users-with-assets/ — для админа
    выдаёт [{id, username, assets: [...]}, …]
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        users = User.objects.filter(is_staff=False)
        data = []
        for u in users:
            assets = Asset.objects.filter(owner=u)
            ser = AssetSerializer(assets, many=True, context={'request': request})
            data.append({
                'id': u.id,
                'username': u.username,
                'assets': ser.data
            })
        return Response(data)
