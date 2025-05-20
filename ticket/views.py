import ghasedak_sms
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

from Config import settings
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

    @action(methods=['post'], permission_classes=[AllowAny], detail=True)
    def ticket_coupon(self, request, pool_id=None, pk=None):
        coupon_code = request.data.get('coupon_code')
        time = jdatetime.datetime.now().togregorian()
        aware_time = timezone.make_aware(time)

        if not coupon_code:
            return Response({"error": "کد کوپن الزامی است."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            coupon = TicketCoupon.objects.get(coupon__iexact=coupon_code, start__lte=aware_time, end__gte=aware_time,
                                              active=True)
            if not coupon.active:
                return Response({"error": "کوپن نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)

            ticket_obj = self.get_object()
            ticket = ticket_obj

            discount_amount = (ticket.price * coupon.discount) // 100
            final_price = ticket.price - discount_amount

            return Response({"discount": discount_amount, "final_price": final_price}, status=status.HTTP_200_OK)

        except TicketCoupon.DoesNotExist:
            return Response({"error": "کوپن یافت نشد."}, status=status.HTTP_404_NOT_FOUND)


class TicketReservationViewSet(ModelViewSet):
    serializer_class = TicketReservationSerializer
    permission_classes = [AllowAny]
    queryset = TicketReservation.objects.all()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        reservation = serializer.save()

        payment = Payment.objects.create(reservation=reservation)

        return Response({
            "reservation_id": reservation.id,
            "payment_id": payment.id,
            "message": "رزرو با موفقیت انجام شد. آماده شروع پرداخت."
        }, status=201)


class PaidTicketsViewSet(ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [AllowAny]  # چون پرداخت ممکنه قبل لاگین انجام شه
    queryset = Payment.objects.all()

    def create(self, request, *args, **kwargs):
        payment_pk = request.data.get('payment_id')
        price = request.data.get('price')

        payment = get_object_or_404(Payment, pk=payment_pk)

        # بررسی پرداخت قبلی
        if payment.paid:
            return Response({"error": "این رزرو قبلاً پرداخت شده است."}, status=status.HTTP_400_BAD_REQUEST)

        if price:
            price = int(price)
            payment.price = price
            payment.save()

        # بررسی نهایی قیمت
        if not payment.price or payment.price <= 0:
            return Response({"error": "قیمت نامعتبر است."}, status=status.HTTP_400_BAD_REQUEST)

        reservation = payment.reservation

        # ساختن callback URL
        callback_url = "http://localhost:4200/ticket-result"

        # ایجاد درخواست پرداخت برای زرین‌پال
        data = {
            "merchant_id": "0ad38487-200a-4563-9edf-66241e005555",
            "amount": payment.price,
            "callback_url": callback_url,
            "description": f"پرداخت برای رزرو با کد {reservation.id}",
        }

        headers = {'content-type': 'application/json'}
        response = requests.post("https://api.zarinpal.com/pg/v4/payment/request.json", json=data, headers=headers)

        if response.status_code == 200:
            res_data = response.json().get("data", {})
            if res_data.get("code") == 100:
                authority = res_data.get("authority")
                payment.authority = authority
                payment.save()

                return Response({
                    "url": f"https://www.zarinpal.com/pg/StartPay/{authority}"
                })
            else:
                return Response({"error": "خطا در دریافت کد پرداخت از زرین‌پال"},
                                status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            return Response({"error": "خطا در اتصال به زرین‌پال"}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=False, methods=['get'])
    def verify(self, request):
        authority = request.query_params.get('Authority')
        status_param = request.query_params.get('Status')

        if not authority or not status_param:
            return Response({"error": "پارامترهای ناقص"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            payment = Payment.objects.get(authority=authority)
        except Payment.DoesNotExist:
            return Response({"error": "تراکنش پیدا نشد"}, status=status.HTTP_404_NOT_FOUND)

        if status_param != 'OK':
            return Response({"error": "وضعیت پرداخت ناموفق بود."}, status=status.HTTP_400_BAD_REQUEST)

        # درخواست تایید به زرین‌پال (دریافت ref_id)
        data = {
            "merchant_id": "0ad38487-200a-4563-9edf-66241e005555",
            "amount": payment.price,
            "authority": authority
        }

        headers = {'content-type': 'application/json'}
        response = requests.post("https://api.zarinpal.com/pg/v4/payment/verify.json", json=data, headers=headers)
        res_data = response.json().get("data", {})

        if response.status_code == 200 and res_data.get("code") in [100, 101]:
            if not payment.paid:
                payment.paid = True
                payment.ref_id = res_data.get("ref_id")
                payment.save()

            # فقط اگر sms_sent=False بود پیامک ارسال بشه
            if not payment.sms_sent:
                reservation = payment.reservation
                code = reservation.code
                phone = reservation.phone_number
                full_name = reservation.full_name

                try:
                    sms_api = ghasedak_sms.Ghasedak(settings.GHASEDAK_API_KEY)
                    sms_api.send_single_sms(
                        ghasedak_sms.SendSingleSmsInput(
                            message=f'جناب {full_name}، شماره بلیط شما {code} می‌باشد.',
                            receptor=phone,
                            line_number='30005088',
                        )
                    )
                    payment.sms_sent = True
                    payment.save()
                except ghasedak_sms.error.ApiException as e:
                    return Response({'error': f'پرداخت تایید شد ولی پیامک ارسال نشد: {str(e)}'},
                                    status=status.HTTP_206_PARTIAL_CONTENT)

            return Response({'status': 'success', 'ref_id': payment.ref_id}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'تأیید پرداخت از طرف زرین‌پال ناموفق بود'}, status=status.HTTP_400_BAD_REQUEST)
