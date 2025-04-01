import jdatetime
from django.shortcuts import render, get_object_or_404
from django.utils import timezone
from rest_framework.decorators import action
from rest_framework.exceptions import NotFound
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import *
from rest_framework import status
from .serializers import *
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate


# Create your views here.

class PoolTicketsViewSet(ModelViewSet):
    serializer_class = PoolTicketSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        pool_id = self.kwargs.get('pool_id')
        if not pool_id:
            return PoolTicket.objects.none()
        return PoolTicket.objects.filter(pool_id=pool_id).select_related('pool')
