from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, RegisterView, UserViewSet

router = DefaultRouter()
router.register(r'assets', AssetViewSet, basename='asset')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('', include(router.urls)),
]


from django.views.generic import DetailView
from assets.models import Asset

urlpatterns += [
    path('asset/<uuid:pk>/', DetailView.as_view(
        model=Asset,
        template_name='assets/asset_detail.html'
    ), name='asset-detail-web'),
]
