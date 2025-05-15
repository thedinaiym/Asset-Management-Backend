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
            serializer.save()
        else:
            serializer.save(owner=None, status='pending', pending_user=user)

    def partial_update(self, request, *args, **kwargs):
        if not request.user.is_staff:
            return Response(status=status.HTTP_403_FORBIDDEN)
        return super().partial_update(request, *args, **kwargs)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='approve')
    def approve(self, request, pk=None):
        asset = self.get_object()
        asset.status = 'approved'
        asset.pending_user = None
        asset.save()
        return Response(self.get_serializer(asset).data)

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated], url_path='deny')
    def deny(self, request, pk=None):
        asset = self.get_object()
        asset.status = 'denied'
        asset.pending_user = None
        asset.save()
        return Response(self.get_serializer(asset).data)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated], url_path='qr', url_name='asset-qr')
    def qr(self, request, pk=None):
        asset = self.get_object()
        url = request.build_absolute_uri(reverse('asset-detail-web', args=[asset.id]))
        img = qrcode.make(url)
        buf = io.BytesIO()
        img.save(buf, format='PNG')
        buf.seek(0)
        return HttpResponse(buf, content_type='image/png')

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated], url_path='qr-pdf', url_name='asset-qr-pdf')
    def qr_pdf(self, request, pk=None):
        asset = self.get_object()
        url = request.build_absolute_uri(reverse('asset-detail-web', args=[asset.id]))
        img = qrcode.make(url)
        buf_img = io.BytesIO()
        img.save(buf_img, format='PNG')
        buf_img.seek(0)
        buf_pdf = io.BytesIO()
        p = canvas.Canvas(buf_pdf)
        p.drawInlineImage(buf_img, 100, 500, 200, 200)
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
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)