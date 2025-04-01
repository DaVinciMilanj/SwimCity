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

from .models import RequestPrivateClass
from .serializers import *
from .permissions import *
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate


# Create your views here.

class PublicPoolViewSet(ModelViewSet):
    serializer_class = PoolsSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Pool.objects.filter(active=True, status='public')


class EduPoolViewSet(ModelViewSet):
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

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def check_coupon(self, request, pools_pk=None, pk=None):
        coupon_code = request.data.get('coupon_code')
        time = jdatetime.datetime.now()

        if not coupon_code:
            return Response({"error": "کد کوپن الزامی است."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            coupon = Coupon.objects.get(code__iexact=coupon_code, start__lte=time, end__gte=time, active=True)

            # بررسی دستی اعتبار کوپن (به‌جای is_valid)
            if not coupon.active:
                return Response({"error": "کوپن نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)

            class_obj = self.get_object()
            discount_amount = (class_obj.price * coupon.discount) // 100  # محاسبه تخفیف
            final_price = class_obj.price - discount_amount  # قیمت نهایی

            return Response({
                "discount": discount_amount,
                "final_price": final_price
            }, status=status.HTTP_200_OK)

        except Coupon.DoesNotExist:
            return Response({"error": "کوپن یافت نشد."}, status=status.HTTP_404_NOT_FOUND)


class PaidViewSet(ModelViewSet):
    serializer_class = PaidSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_pk = self.kwargs['course_pk']
        return Paid.objects.filter(course__pk=course_pk, user=self.request.user)

    def create(self, request, *args, **kwargs):
        course_pk = self.kwargs.get('course_pk')
        course = get_object_or_404(Classes, pk=course_pk)

        # بررسی وجود پرداخت قبلی
        paid_instance, created = Paid.objects.get_or_create(
            course=course, user=request.user,
            defaults={'price': course.total_price, 'paid': True}
        )

        # اگر از قبل وجود داشت، همان را برگردان
        if not created:
            serializer = self.get_serializer(paid_instance)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # اگر کاربر مبلغ فرستاده باشد، آن را به‌روز کند
        if 'price' in request.data:
            paid_instance.price = request.data['price']
            paid_instance.save()

        serializer = self.get_serializer(paid_instance)
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


# ----------------------------------------------------------------------------------------------------------------------
class MyCourseViewSet(ModelViewSet):
    serializer_class = MyCourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        now = timezone.now()
        queryset = StartClass.objects.filter(student=self.request.user, course__start__lte=now,
                                             course__end__gte=now).select_related("course")

        if not queryset.exists():
            raise NotFound("دوره‌ای برای شما یافت نشد.")

        return queryset
