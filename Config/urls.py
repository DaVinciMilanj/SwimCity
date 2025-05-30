"""
URL configuration for Config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from Config.sitemaps import sitemaps
from django.http import HttpResponse


# schema_view = get_schema_view(
#    openapi.Info(
#       title="Your API Title",  # عنوان API خود را اینجا بنویسید
#       default_version='v1',  # ورژن API که معمولاً 'v1' است
#       description="SwimCity API",  # توضیح کوتاهی از API بنویسید
#       terms_of_service="https://www.google.com/policies/terms/",  # لینک به قوانین و مقررات
#       contact=openapi.Contact(email="radinmilani2005@gmail.com"),  # ایمیل تماس
#       license=openapi.License(name="BSD License"),  # لایسنس API، مثل BSD یا MIT
#    ),
#    public=True,  # نمایش عمومی API
#    permission_classes=(permissions.AllowAny,),  # همه کاربران به API دسترسی دارند
# )

def robots_txt(request):
    return HttpResponse(
        "User-agent: *\n"
        "Disallow: /admin/\n"
        "Disallow: /api/\n"
        "Sitemap: https://qahramananemrooz.com/sitemap.xml",
        content_type="text/plain"
    )


urlpatterns = [
    path('admin/admin/', admin.site.urls),
    # path('i18n/', include('django.conf.urls.i18n')),
    path('api/accounts/', include('accounts.urls', namespace='accounts')),
    path('api/pools/', include('pool.urls', namespace='pools')),
    path('api/ticket/', include('ticket.urls', namespace='ticket')),
    path("__debug__/", include("debug_toolbar.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="sitemap"),
    path("robots.txt", robots_txt),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
