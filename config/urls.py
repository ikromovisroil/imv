from django.contrib import admin
from django.urls import path,include
from django.urls import re_path as url
from django.views.static import serve
from django.conf.urls.static import static
from django.conf import settings

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('main.urls')),
]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if not settings.DEBUG:
    urlpatterns += url(r'^media/(?P<path>.*)$', serve,{'document_root': settings.MEDIA_ROOT}),
    urlpatterns += url(r'^static/(?P<path>.*)$', serve,{'document_root': settings.STATIC_ROOT}),