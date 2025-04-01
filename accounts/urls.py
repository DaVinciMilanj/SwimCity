from django.urls import path
from . import views
from rest_framework_nested import routers
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()

router.register('users', views.GetUsersViewSet, basename='users')
router.register('signup', views.SignUpViewSet, basename='signup')
router.register('login', views.LoginViewSet, basename='login')
router.register('profile', views.ProfileViewSet, basename='profile')
router.register('teacher-form', views.TeacherSignUpViewSet, basename='teacher-form')
router.register('teacher', views.TeacherViewList, basename='teacher')
teacher_router = routers.NestedDefaultRouter(router, 'teacher', lookup='teacher')
teacher_router.register('comment', views.CommentTeacherViewSet, basename='teacher-comment')
router.register('forgot-password', views.ForgotPasswordViewSet, basename='forgot-password')

urlpatterns = router.urls + teacher_router.urls + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = 'accounts'
