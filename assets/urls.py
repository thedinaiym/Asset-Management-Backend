# assets/urls.py
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import AssetViewSet, RegisterView, UsersWithAssetsView

router = DefaultRouter()
router.register(r"assets", AssetViewSet, basename="asset")

urlpatterns = [
    path("register/",            RegisterView.as_view(),        name="register"),
    path("users-with-assets/",   UsersWithAssetsView.as_view(), name="users-with-assets"),
    path("", include(router.urls)),
]
