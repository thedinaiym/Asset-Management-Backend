# # asset_management/urls.py
# from django.contrib import admin
# from django.urls import path, include
# from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
# from django.conf import settings
# from django.conf.urls.static import static

# # импортим DetailView и модель
# from django.views.generic import DetailView
# from assets.models import Asset

# urlpatterns = [
#     path('admin/', admin.site.urls),
#     path('api/', include('assets.urls')),
#     path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
#     path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
#     # DetailView для веб-страницы карточки
#     path(
#         'asset/<uuid:pk>/',
#         DetailView.as_view(
#             model=Asset,
#             template_name='assets/asset_detail.html',
#             context_object_name='asset'
#         ),
#         name='asset-detail-web'
#     ),
# ]

# if settings.DEBUG:
#     urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
from django.contrib import admin
from django.urls import path, include, re_path
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import (
    TokenObtainPairView, TokenRefreshView
)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('assets.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)