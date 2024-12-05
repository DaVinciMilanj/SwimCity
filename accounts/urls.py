from django.urls import path
from . import views
from rest_framework_nested import routers
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()

router.register('signup', views.SignUpViewSet, basename='signup')
router.register('login', views.LoginViewSet, basename='login')
router.register('profile', views.ProfileViewSet, basename='profile')
router.register('formteacher', views.TeacherSignUpViewSet, basename='formteacher')
router.register('teacher', views.TeacherViewList, basename='teacher')
router.register('forgot-password', views.ForgotPasswordViewSet, basename='forgot-password')

urlpatterns = router.urls

# urlpatterns = [
#     path('' , views.user_details , name='user_details')
#
# ]


app_name = 'accounts'
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
