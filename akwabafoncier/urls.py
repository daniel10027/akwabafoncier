from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from core.views import service_worker

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sw.js', service_worker, name='service_worker'),
    path('', include('core.urls')),
    path('auth/', include('utilisateurs.urls')),
    path('dashboard/', include('foncier.urls')),
    path('cartographie/', include('cartographie.urls')),
    path('paiements/', include('paiements.urls')),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT) \
  + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
