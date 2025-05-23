from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('election/', include('election.urls')),
    path('', TemplateView.as_view(template_name='index.html'), name='home'),
    path('accessibility/', TemplateView.as_view(template_name='accessibility.html'), name='accessibility'),
]

# Adiciona as URLs para servir arquivos de mídia durante o desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)