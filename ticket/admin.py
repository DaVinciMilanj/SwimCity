from django.contrib import admin
from django_jalali.admin.filters import JDateFieldListFilter

from .models import PoolTicket, TicketReservation, Payment, TicketCoupon


@admin.register(PoolTicket)
class PoolTicketAdmin(admin.ModelAdmin):
    list_display = ('pool', 'description', 'price', 'discount_amount', 'final_price', 'created_at_formatted')
    list_filter = ('pool',)
    search_fields = ('pool__name', 'description')
    readonly_fields = ('created_at_formatted', 'modified_at_formatted')

    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%Y-%m-%d  /  %H:%M:%S')

    created_at_formatted.admin_order_field = 'created_at'
    created_at_formatted.short_description = 'زمان ایجاد'

    def modified_at_formatted(self, obj):
        return obj.modified_at.strftime('%Y-%m-%d  /  %H:%M:%S')

    modified_at_formatted.admin_order_field = 'modified_at'
    modified_at_formatted.short_description = 'آخرین تغییر'


@admin.register(TicketReservation)
class TicketReservationAdmin(admin.ModelAdmin):
    list_display = (
        'full_name', 'phone_number', 'ticket', 'code',
        'payment_status', 'created_at_formatted',
        'entrance_time_formatted', 'exit_time_formatted',
        'extra_cost_display'
    )
    list_filter = ('ticket',)
    search_fields = ('full_name', 'phone_number', 'code', 'closet_code')
    readonly_fields = ('code', 'quantity','created_at_formatted','extra_cost_display' )

    def entrance_time_formatted(self, obj):
        if obj.entrance_time:
            return obj.entrance_time.strftime('%H:%M')
        return "—"
    entrance_time_formatted.short_description = 'ساعت ورود'

    def exit_time_formatted(self, obj):
        if obj.exit_time:
            return obj.exit_time.strftime('%H:%M')
        return "—"
    exit_time_formatted.short_description = 'ساعت خروج'

    def created_at_formatted(self, obj):
        return obj.created_at.strftime('%Y-%m-%d  /  %H:%M:%S')
    created_at_formatted.admin_order_field = 'created_at'
    created_at_formatted.short_description = 'زمان ایجاد'

    def extra_cost_display(self, obj):
        return f"{obj.extra_cost:,} تومان" if obj.entrance_time and obj.exit_time else "—"
    extra_cost_display.short_description = 'مبلغ اضافه‌تر بابت زمان بیشتر'

    def payment_status(self, obj):
        payment = Payment.objects.filter(reservation=obj).first()
        if payment:
            return "پرداخت شده ✅" if payment.paid else "پرداخت نشده ❌"
        return "پرداخت نشده ❌"
    payment_status.short_description = 'وضعیت پرداخت'


class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'paid', 'price', 'ref_id', 'created_at')
    list_filter = ('paid',)
    search_fields = ('reservation__full_name', 'ref_id')
    readonly_fields = ('price', 'created_at')


admin.site.register(Payment, PaymentAdmin)


#
class CouponAdmin(admin.ModelAdmin):
    list_display = ['coupon', 'start', 'end', 'discount', 'active']
    list_filter = (
        ('coupon', JDateFieldListFilter),
    )


admin.site.register(TicketCoupon, CouponAdmin)
