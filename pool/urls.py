from django.urls import path
from . import views
from rest_framework_nested import routers
from django.conf import settings
from django.conf.urls.static import static

router = routers.DefaultRouter()

router.register('pool', views.EduPoolViewSet, basename='pools')
router.register('public-pool' , views.PublicPoolViewSet , basename='public-pool')
router.register('my-course' , views.MyCourseViewSet , basename='my-course')
pool_routers = routers.NestedDefaultRouter(router, 'pool', lookup='pools')

pool_routers.register('course', views.CourseViewSet, basename='pools-course')
course_routers = routers.NestedDefaultRouter(pool_routers, 'course', lookup='course')

router.register('private-class' , views.PrivateClassRequestViewSet , basename='private-class')
router.register('create-private-class' , views.CreatePrivateClassViewSet , basename='create-private-class')
course_routers.register('paid', views.PaidViewSet, basename='course-paid')


urlpatterns = router.urls + pool_routers.urls + course_routers.urls

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

app_name = 'pools'
