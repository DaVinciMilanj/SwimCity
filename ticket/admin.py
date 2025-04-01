from django.contrib import admin
from .models import PoolTicket, TicketReservation, Payment


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
        'full_name', 'phone_number', 'ticket', 'code', 'payment_status', 'created_at', 'entrance_time', 'exit_time')
    list_filter = ('ticket',)
    search_fields = ('full_name', 'phone_number', 'code')
    readonly_fields = ('code', 'created_at')

    def payment_status(self, obj):
        payment = Payment.objects.filter(reservation=obj).first()
        if payment:
            return "پرداخت شده ✅" if payment.paid else "پرداخت نشده ❌"
        return "پرداخت نشده ❌"

    payment_status.short_description = 'وضعیت پرداخت'


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('reservation', 'paid', 'price', 'ref_id', 'created_at')
    list_filter = ('paid',)
    search_fields = ('reservation__full_name', 'ref_id')
    readonly_fields = ('price', 'created_at')
