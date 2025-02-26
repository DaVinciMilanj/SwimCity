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

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('i18n/', include('django.conf.urls.i18n')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('pools/' , include('pool.urls' , namespace='pools')),
    path("__debug__/", include("debug_toolbar.urls")),


]

urlpatterns += i18n_patterns(
    path('admin/', admin.site.urls),
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
