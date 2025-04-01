import random
from django.db import models
from django_jalali.db import models as jmodels
from pool.models import Pool


# Create your models here.
class PoolTicket(models.Model):
    pool = models.ForeignKey(Pool, on_delete=models.DO_NOTHING, related_name='pool_tickets',
                             limit_choices_to={'status': 'public'}, verbose_name='استخر')
    price = models.PositiveBigIntegerField(verbose_name='قیمت')
    discount_amount = models.PositiveBigIntegerField(default=0, verbose_name='مبلغ تخفیف ')
    description = models.CharField(max_length=250, verbose_name='توضیحات')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='ساخته شده')
    modified_at = models.DateTimeField(auto_now=True, verbose_name='تغییر داده شده')

    class Meta:
        verbose_name = "بلیط"
        verbose_name_plural = "بلیط ها"

    def __str__(self):
        return f"{self.pool.name} - {self.description}"

    @property
    def final_price(self):
        return max(self.price - self.discount_amount, 0)



class TicketReservation(models.Model):
    ticket = models.ForeignKey(PoolTicket, on_delete=models.DO_NOTHING, verbose_name='بلیط',
                               related_name='reserve_tickets')
    full_name = models.CharField(max_length=250, verbose_name='نام و نام خانوادگی')
    phone_number = models.CharField(max_length=15, verbose_name='شماره تلفن')
    code = models.CharField(max_length=6, unique=True, editable=False, verbose_name='کد ورود')
    entrance_time = jmodels.jDateTimeField(null=True, blank=True, verbose_name='ساعت ورود')
    exit_time = jmodels.jDateTimeField(null=True, blank=True, verbose_name='ساعت خروج')
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ خرید')

    class Meta:
        verbose_name = "بلیط کاربر"
        verbose_name_plural = "بلیط کاربران"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = f"{random.randint(0, 999999):06}"
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.full_name} - {self.ticket}"


class Payment(models.Model):
    reservation = models.OneToOneField(TicketReservation, on_delete=models.CASCADE,
                                       related_name='payment', verbose_name='رزرو')
    paid = models.BooleanField(default=False, verbose_name='پرداخت شده')
    ref_id = models.CharField(max_length=50, null=True, blank=True, verbose_name='شماره تراکنش')
    price = models.PositiveBigIntegerField(default=0)
    created_at = jmodels.jDateTimeField(auto_now_add=True, verbose_name='تاریخ پرداخت')

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"

    def __str__(self):
        return f"{self.reservation} - {'پرداخت شده' if self.paid else 'پرداخت نشده'}"

    def save(self, *args, **kwargs):
        total_price = self.reservation.ticket.final_price
        if self.price == 0:
            self.price = total_price
        super().save(*args, **kwargs)
