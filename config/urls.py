from django.conf.urls import include
from django.contrib.auth import views as auth_views
from django.urls import path, re_path
from django.views.static import serve
from django.contrib import admin
from drf_yasg.views import get_schema_view
from drf_yasg import openapi
from rest_framework import permissions

from config.static import STATIC_ROOT, MEDIA_ROOT
from config.base import DEBUG


APP_URLS = [
    path('', include('core.urls')),
    path('data/', include('data.urls')),
    path('', include('learning.urls')),
    path('', include('user.urls')),
]

DJANGO_URLS = [
    path('login/', auth_views.LoginView.as_view(template_name='admin/login.html'), name='login'),
    path('admin/', admin.site.urls, name='admin'),
    path("ckeditor5/", include('django_ckeditor_5.urls'), name="ck_editor_5_upload_file"),
]

STATIC_URLS = [
    re_path(r'^media/(?P<path>.*)$', serve, { 'document_root': MEDIA_ROOT }),
    re_path(r'^static/(?P<path>.*)$', serve, { 'document_root': STATIC_ROOT }),
]

if DEBUG:
    schema_view = get_schema_view(
        openapi.Info(
            title="CAT API Documentation",
            default_version='v1',
        ),
        public=True,
        permission_classes=(permissions.AllowAny,),
    )

    swagger_with_ui_path = path(
        route='__docs__/', 
        view=schema_view.with_ui('swagger', cache_timeout=0), 
        name='schema-swagger-ui'
    )
    
    swagger_without_ui_path = path(
        route='__docs__/json/', 
        view=schema_view.without_ui(cache_timeout=0), 
        name='schema-json'
    )
    
    DJANGO_URLS += [swagger_with_ui_path, swagger_without_ui_path]

urlpatterns = APP_URLS + DJANGO_URLS + STATIC_URLS

APP_NAME = "CAT API"
admin.site.site_header = f"{APP_NAME} Admin"
admin.site.site_title = f"{APP_NAME} Admin"
