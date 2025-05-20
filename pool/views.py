import jdatetime
import requests
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
        price = request.data.get('price') or course.total_price
        price = int(price)

        # ایجاد فیش جدید
        paid_instance = Paid.objects.create(
            course=course,
            user=request.user,
            price=price,
            paid=False
        )

        callback_url = f"http://localhost:4200/payment-result"
        data = {
            "merchant_id": "0ad38487-200a-4563-9edf-66241e005555",
            "amount": price,
            "callback_url": callback_url,
            "description": f"پرداخت برای دوره {course.course_start.course_code}",
        }

        headers = {'content-type': 'application/json'}
        response = requests.post("https://api.zarinpal.com/pg/v4/payment/request.json", json=data, headers=headers)

        res_data = response.json().get("data", {})

        if response.status_code == 200 and res_data.get("code") == 100:
            # ذخیره authority
            paid_instance.authority = res_data['authority']
            paid_instance.save()

            return Response({
                "url": f"https://www.zarinpal.com/pg/StartPay/{res_data['authority']}"
            })
        else:
            return Response({"error": "خطا در اتصال به زرین‌پال"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='verify')
    def verify(self, request, pools_pk=None, course_pk=None):
        authority = request.query_params.get('Authority')
        status_param = request.query_params.get('Status')

        if status_param != 'OK':
            return Response({'status': 'failed', 'message': 'پرداخت توسط کاربر لغو شد'}, status=400)
        print("Received authority:", authority)
        # فیش را بر اساس authority پیدا کن
        paid_instance = get_object_or_404(Paid, authority=authority)

        data = {
            "merchant_id": "0ad38487-200a-4563-9edf-66241e005555",
            "amount": paid_instance.price,
            "authority": authority
        }

        response = requests.post("https://api.zarinpal.com/pg/v4/payment/verify.json", json=data)
        res_data = response.json().get("data", {})

        if response.status_code == 200 and res_data.get("code") in [100, 101]:
            print("Verify called with authority:", authority)
            paid_instance.paid = True
            paid_instance.ref_id = res_data.get("ref_id")
            paid_instance.save()
            return Response({'status': 'success', 'ref_id': res_data.get("ref_id")})
        else:
            return Response({'status': 'failed', 'message': 'تأیید پرداخت ناموفق بود'}, status=400)


# class GetMyPaidViewSet(ModelViewSet):
#     permission_classes = [IsAuthenticated]
#     serializer_class = PaidSerializer
#
#     def get_queryset(self):
#         authority = self.request.query_params.get('authority')
#         return Paid.objects.filter(user=self.request.user, authority=authority, paid=True)
#

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


# ----------------------------------------------------------------------------------

class PaidPrivateClass(ModelViewSet):
    serializer_class = PaidPrivateClassSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Paid.objects.filter(private_class__pk=self.request.data.get('private_class_pk'), user=self.request.user)

    def create(self, request, *args, **kwargs):
        private_class_pk = self.request.data.get('private_class_pk')
        private_class = get_object_or_404(PrivateClass, pk=private_class_pk)
        price = request.data.get('price') or private_class.total_price
        price = int(price)

        # ایجاد فیش جدید
        paid_instance = Paid.objects.create(
            private_class=private_class,
            user=request.user,
            price=price,
            paid=False
        )

        callback_url = "http://localhost:4200/private-payment"
        data = {
            "merchant_id": "0ad38487-200a-4563-9edf-66241e005555",
            "amount": price,
            "callback_url": callback_url,
            "description": f"پرداخت کلاس خصوصی {private_class}",
        }

        headers = {'content-type': 'application/json'}
        response = requests.post("https://api.zarinpal.com/pg/v4/payment/request.json", json=data, headers=headers)
        res_data = response.json().get("data", {})

        if response.status_code == 200 and res_data.get("code") == 100:
            paid_instance.authority = res_data['authority']
            paid_instance.save()

            return Response({
                "url": f"https://www.zarinpal.com/pg/StartPay/{res_data['authority']}"
            })
        else:
            return Response({"error": "خطا در اتصال به زرین‌پال"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'], url_path='verify')
    def verify(self, request, pools_pk=None, private_class_pk=None):
        authority = request.query_params.get('Authority')
        status_param = request.query_params.get('Status')

        if status_param != 'OK':
            return Response({'status': 'failed', 'message': 'پرداخت توسط کاربر لغو شد'}, status=400)

        paid_instance = get_object_or_404(Paid, authority=authority)

        data = {
            "merchant_id": "0ad38487-200a-4563-9edf-66241e005555",
            "amount": paid_instance.price,
            "authority": authority
        }

        response = requests.post("https://api.zarinpal.com/pg/v4/payment/verify.json", json=data)
        res_data = response.json().get("data", {})

        if response.status_code == 200 and res_data.get("code") in [100, 101]:
            paid_instance.paid = True
            paid_instance.ref_id = res_data.get("ref_id")
            paid_instance.save()
            return Response({'status': 'success', 'ref_id': res_data.get("ref_id")})
        else:
            return Response({'status': 'failed', 'message': 'تأیید پرداخت ناموفق بود'}, status=400)