# assets/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    AssetViewSet,
    RegisterView,
    UsersWithAssetsView,
    ProfileView,
    ChangePasswordView,
)

router = DefaultRouter()
router.register(r"assets", AssetViewSet, basename="asset")

urlpatterns = [
    path("register/",                 RegisterView.as_view(),        name="register"),
    path("users-with-assets/",        UsersWithAssetsView.as_view(), name="users-with-assets"),
    path("profile/",                  ProfileView.as_view(),         name="profile"),
    path("profile/change-password/",  ChangePasswordView.as_view(),  name="change-password"),
    path("", include(router.urls)),
]
