"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/6.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.contrib.admin import site as admin_site

admin_site.site_header = "智善TIC人才测评体系管理系统"
admin_site.site_title = "智善TIC人才测评体系"
admin_site.index_title = "管理控制台"

from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from django.views.generic import TemplateView
from django.http import FileResponse
from django.shortcuts import render
import os


def spa_view(request, path=''):
    """Serve the Vue SPA for client-side routing"""
    index_path = os.path.join(settings.BASE_DIR, 'frontend', 'dist', 'index.html')
    try:
        return FileResponse(open(index_path, 'rb'), content_type='text/html')
    except FileNotFoundError:
        from django.http import HttpResponseNotFound
        return HttpResponseNotFound('前端资源未构建，请运行 npm run build')



def qrcode_page(request):
    from django.apps import apps
    AT = apps.get_model("assessment", "AssessmentTemplate")
    templates = AT.objects.filter(is_active=True).order_by("name")
    return render(request, "assessment/qrcode.html", {
        "exam_templates": templates,
        "entry_url": "/assessment/enter/",
        "site_url": request.build_absolute_uri('/').rstrip('/'),
    })


urlpatterns = [
    path('admin/', admin.site.urls),
    path('exam-qrcode/', qrcode_page, name='exam_qrcode'),
    # Health check (returns 200 for Railway health probes)
    path('health/', lambda r: __import__('django.http').http.HttpResponse(b'OK')),
    # Root: serve Vue SPA
    path('', spa_view, name='home'),
    # API
    path('api/', include('assessment.urls_api')),
    # Django dashboard
    path('dashboard/', include('assessment.urls_dashboard')),
    # Employee assessment flow
    path('', include('assessment.urls')),
    # Corporate pages (Django templates)
    path('', include('assessment.urls_corporate')),
    # SPA catch-all: serve Vue app for /login, /register, etc.
    re_path(r'^(?!static/|media/|admin/|api/|dashboard/).*$', spa_view, name='spa'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


