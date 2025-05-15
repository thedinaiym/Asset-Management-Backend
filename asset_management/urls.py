# asset_management/urls.py
from django.contrib import admin
from django.urls import path, include
from django.http import HttpResponse
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

# простой ответ на GET /
def home(request):
    return HttpResponse("Сервис Asset Management запущен!")

urlpatterns = [
    # корень
    path('', home, name='home'),
    # либо сразу редирект на админку/API:
    # path('', RedirectView.as_view(url='/admin/', permanent=False)),
    
    path('admin/', admin.site.urls),
    path('api/', include('assets.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # веб-карточка
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

# отдача media-файлов и статических (чтобы не было 404 на /media/…)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
