from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, RegisterView, ProfileView, ChangePasswordView

router = DefaultRouter()
router.register(r'assets', AssetViewSet, basename='asset')
# router.register(r'users', UserViewSet, basename='user')  # Удалили

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('', include(router.urls)),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/change-password/', ChangePasswordView.as_view(), name='change-password'),
]
