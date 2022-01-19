from django.conf import settings
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.urls import path, include
from django.conf.urls.static import static
from nblog1.sitemaps import BlogSitemap, PostSitemap


sitemaps = {
    'posts': PostSitemap,
    'blog': BlogSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('sitemap.xml/', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
    path('', include('nblog1.urls',namespace='nblog1')),
    path('ckeditor/', include('ckeditor_uploader.urls')),
    path('captcha/', include('captcha.urls')),
]


urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)