"""
URL configuration for huali_website project.

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
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

from main.upload_views import richtext_image_upload
from operations.views import private_inquiry_attachment, security_center
from operations.redirects import old_news_url, old_product_url

admin.site.site_header = '华丽电器内容管理'
admin.site.site_title = '华丽电器内容管理'
admin.site.index_title = '内容运营后台'

urlpatterns = [
    path('products/<str:model>', old_product_url, name='old-product-url'),
    path('products/<str:model>/', old_product_url),
    path('news/<slug:slug>', old_news_url, name='old-news-url'),
    path('news/<slug:slug>/', old_news_url),
    path('admin/security/', include('operations.urls')),
    path('admin/security-center/', security_center, name='security-center-shortcut'),
    path('admin/', admin.site.urls),
    path('admin/content-image-upload/<str:kind>/', richtext_image_upload, name='content-image-upload'),
    path('admin/private/inquiries/<int:pk>/attachment/', private_inquiry_attachment, name='admin-private-inquiry-attachment'),
    path('api/v1/', include('main.api')),
    path('api/', include('main.urls')),
]

if settings.DEBUG:
    urlpatterns += [
        path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
        path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
        path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    ]
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
