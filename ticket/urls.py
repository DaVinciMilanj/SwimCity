from django.urls import path
from . import views
from rest_framework_nested import routers

from .views import *

app_name = 'ticket'

router = routers.DefaultRouter()
router.register(r'pool/(?P<pool_id>\d+)/tickets', PoolTicketsViewSet, basename='pool-tickets')
router.register('reserve-ticket', TicketReservationViewSet, basename='reserve-ticket')
router.register('paid-ticket', PaidTicketsViewSet, basename='paid-ticket')

urlpatterns = router.urls
