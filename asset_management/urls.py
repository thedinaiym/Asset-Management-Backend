# asset_management/urls.py

from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.generic import DetailView
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from assets.models import Asset

# Простая заглушка на корень
def home(request):
    return HttpResponse("Сервис Asset Management запущен!")

urlpatterns = [
    # корень
    path('', home, name='home'),

    # админка
    path('admin/', admin.site.urls),

    # JWT-токены
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # DRF-маршруты
    path('api/', include('assets.urls')),

    # веб-деталка (HTML-карточка) через DetailView
    path(
        'asset/<uuid:pk>/',
        DetailView.as_view(
            model=Asset,
            template_name='assets/asset_detail.html',
            context_object_name='asset'
        ),
        name='asset-detail-web'
    ),
]

# WhiteNoise уже отдаёт STATIC_URL, поэтому не добавляем static() для статики

# Но для MEDIA_URL (фото) оставляем Django-статик
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
