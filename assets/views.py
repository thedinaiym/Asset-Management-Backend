from django.contrib.auth import get_user_model
from rest_framework import viewsets, generics, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.response import Response

from .models import Asset
from .serializers import (
    AssetSerializer,
    RegisterSerializer,
    UserSerializer,
    UserWithAssetsSerializer
)

User = get_user_model()


class RegisterView(generics.CreateAPIView):
    """
    POST /api/register/
    """
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    permission_classes = []  # разрещаем всем


class AssetViewSet(viewsets.ModelViewSet):
    """
    - Обычные юзеры видят только свои assets
    - Админы видят все и могут фильтровать ?owner=<id>
    - Админ может POST approve/deny
    """
    queryset = Asset.objects.all()
    serializer_class = AssetSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = super().get_queryset()
        user = self.request.user

        if user.is_staff:
            owner_id = self.request.query_params.get('owner')
            if owner_id:
                qs = qs.filter(owner__id=owner_id)
        else:
            qs = qs.filter(owner=user)

        return qs

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def approve(self, request, pk=None):
        asset = self.get_object()
        asset.status = Asset.Status.ASSIGNED
        asset.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'], permission_classes=[IsAdminUser])
    def deny(self, request, pk=None):
        asset = self.get_object()
        asset.status = Asset.Status.FREE
        asset.pending_user = None
        asset.owner = None
        asset.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['get'], permission_classes=[IsAuthenticated])
    def qr(self, request, pk=None):
        asset = self.get_object()
        # только для assigned
        if asset.status != Asset.Status.ASSIGNED:
            return Response(
                {'detail': 'QR available only for assigned assets.'},
                status=status.HTTP_400_BAD_REQUEST
            )

        # допустим, у вас есть метод generate_qr_pdf()
        pdf_bytes = asset.generate_qr_pdf()  # возвращает bytes 
        return Response(pdf_bytes, content_type='application/pdf')


class UsersWithAssetsView(generics.ListAPIView):
    """
    GET /api/users-with-assets/
    Админ получает непустой список всех не-админов вместе с их активными assets
    """
    permission_classes = [IsAuthenticated, IsAdminUser]
    serializer_class = UserWithAssetsSerializer

    def get_queryset(self):
        # только не-админы
        return User.objects.filter(is_staff=False).prefetch_related('asset_set')
