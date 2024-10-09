from django.urls import path
from . import views
from rest_framework_nested import routers
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()

router.register('signup', views.SignUpViewSet, basename='signup')
router.register('login', views.LoginViewSet, basename='login')
router.register('profile', views.ProfileViewSet, basename='profile')

urlpatterns = router.urls

# urlpatterns = [
#     path('' , views.user_details , name='user_details')
#
# ]


app_name = 'accounts'
