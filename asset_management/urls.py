# asset_management/urls.py

from django.contrib import admin
from django.urls import path, include, re_path
from django.views.generic import DetailView, RedirectView
from django.http import HttpResponse
from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from assets.models import Asset
from assets import views  # чтобы DRF-роуты подхватились

# Простой приветственный вьюхер на /
def home(request):
    return HttpResponse("Сервис Asset Management запущен!")

urlpatterns = [
    # Главная страница
    path('', home, name='home'),
    # или вместо home можно сразу редиректить:
    # path('', RedirectView.as_view(url='/admin/', permanent=False)),

    # Админка
    path('admin/', admin.site.urls),

    # JWT-токены
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    # Основные DRF-роуты из assets/urls.py
    path('api/', include('assets.urls')),

    # Веб-карточка (HTML) для DetailView
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

# Отдаём статику и медиа всегда (не только в DEBUG)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
