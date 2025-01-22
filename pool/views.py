from django.shortcuts import render, get_object_or_404
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import *
from rest_framework import status

from .models import RequestPrivateClass
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


class PrivateClassRequestViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return RequestPrivateClassReadSerializer
        return RequestPrivateClassSerializer

    def get_queryset(self):
        if self.request.user.status == CustomUser.STATUS_CUSTOMUSER_TEACHER:
            return RequestPrivateClass.objects.filter(teacher=self.request.user)
        return RequestPrivateClass.objects.filter(user=self.request.user)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()

        if instance.user != request.user:
            return Response({'detail': 'You do not have permission to delete this request.'},
                            status=status.HTTP_403_FORBIDDEN)

        self.perform_destroy(instance)
        return Response({'detail': 'Request deleted.'}, status=status.HTTP_200_OK)

    def create(self, request, *args, **kwargs):
        data = request.data
        teacher_id = data.get('teacher')  # دریافت ID معلم
        try:
            teacher = CustomUser.objects.get(id=teacher_id)  # شیء Teacher
            data['teacher'] = teacher.id  # ID کاربر مرتبط با Teacher
        except CustomUser.DoesNotExist:
            return Response({'detail': 'Invalid teacher ID'}, status=status.HTTP_400_BAD_REQUEST)

        serializer = self.get_serializer(data=data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def accept(self, request, pk=None):
        instance = self.get_object()

        if request.user.status != CustomUser.STATUS_CUSTOMUSER_TEACHER:
            return Response({'detail': 'You do not have permission to accept this request.'},
                            status=status.HTTP_403_FORBIDDEN)

        instance.acceptation = True
        instance.save()
        return Response({'detail': 'Request accepted.'}, status=status.HTTP_200_OK)

    @action(detail=True, methods=['patch'], permission_classes=[IsAuthenticated])
    def reject(self, request, pk=None):
        instance = self.get_object()

        if request.user.status != CustomUser.STATUS_CUSTOMUSER_TEACHER:
            return Response({'detail': 'You do not have permission to reject this request.'},
                            status=status.HTTP_403_FORBIDDEN)

        instance.acceptation = False
        instance.save()
        return Response({'detail': 'Request rejected.'}, status=status.HTTP_200_OK)


class CreatePrivateClassViewSet(ModelViewSet):
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.action in ['list', 'retrieve']:
            return ShowPrivateClassSerializer
        return CreatePrivateClassSerializer

    def get_queryset(self):
        if self.request.user.status == CustomUser.STATUS_CUSTOMUSER_TEACHER:
            return PrivateClass.objects.filter(teacher=self.request.user)
        return PrivateClass.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(teacher=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
