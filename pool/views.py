from django.shortcuts import render, get_object_or_404
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import *
from rest_framework import status
from .serializers import *
from .permissions import *
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate


# Create your views here.


class PoolViewSet(ModelViewSet):
    serializer_class = PoolsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Pool.objects.filter(active=True, status='education')


class CourseViewSet(ModelViewSet):
    serializer_class = CoursesSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        pools_pk = self.kwargs['pools_pk']
        queryset = Classes.objects.select_related('course_start', 'teacher').filter(
            active=True,
            course_start__pool=pools_pk
        )
        return queryset


class PaidViewSet(ModelViewSet):
    serializer_class = PaidSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_pk = self.kwargs['course_pk']
        return Paid.objects.filter(course__pk=course_pk, user=self.request.user)

    def create(self, request, *args, **kwargs):
        course_pk = self.kwargs.get('course_pk')
        course = Classes.objects.get(pk=course_pk)

        duplicate_paid = Paid.objects.filter(course=course, user=request.user).first()

        if duplicate_paid:
            serializer = self.get_serializer(duplicate_paid)
            return Response(serializer.data, status=status.HTTP_200_OK)

        paid = Paid.objects.create(
            course=course, user=request.user, paid=False
        )
        paid.save()

        serializer = self.get_serializer(paid)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
