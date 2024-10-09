from django.urls import path
from . import views
from rest_framework_nested import routers
from rest_framework.authtoken.views import obtain_auth_token

router = routers.DefaultRouter()

router.register('pool' , views.PoolViewSet , basename='pools')
pool_routers = routers.NestedDefaultRouter(router , 'pool' , lookup='pools')



pool_routers.register('course' , views.CourseViewSet , basename='pools-course')

course_routers = routers.NestedDefaultRouter(pool_routers, 'course', lookup='course')
course_routers.register('paid', views.PaidViewSet, basename='course-paid')


urlpatterns = router.urls + pool_routers.urls + course_routers.urls




app_name = 'pools'
