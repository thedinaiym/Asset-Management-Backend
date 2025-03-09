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
