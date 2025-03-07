from decimal import Decimal

from django.db import models
from django.db.models import Q
from django.db.models.signals import post_save, m2m_changed
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError
from django_jalali.db import models as jmodels
from accounts.models import CustomUser
# Create your models here.
import random

# Create your models here.


STATUS_CUSTOMUSER_DEFAULT = 'default'
STATUS_CUSTOMUSER_TEACHER = 'teacher'
STATUS_CUSTOMUSER_STUDENT = 'student'


class Pool(models.Model):
    STATUS_POOL_PUBLIC = 'public'
    STATUS_POOL_EDUCATION = 'education'
    STATUS = [
        (STATUS_POOL_PUBLIC, 'شیفت عمومی'),
        (STATUS_POOL_EDUCATION, 'شیفت آموزش')
    ]

    STATUS_CUSTOMUSER_FEMALE = 'female'
    STATUS_CUSTOMUSER_MALE = 'male'

    GENDER = (
        (STATUS_CUSTOMUSER_FEMALE, 'زنانه'),
        (STATUS_CUSTOMUSER_MALE, 'مردانه')
    )

    gender = models.CharField(choices=GENDER, max_length=10, null=True, blank=True, verbose_name="جنسیت")
    image = models.ImageField(upload_to='pool_images/', null=True, blank=True, verbose_name="تصویر")
    name = models.CharField(max_length=50, verbose_name="نام استخر")
    active = models.BooleanField(default=True, verbose_name="فعال")
    address = models.TextField(verbose_name="آدرس")
    status = models.CharField(choices=STATUS, max_length=20, blank=True, null=True, verbose_name="وضعیت استخر")

    class Meta:
        verbose_name = "استخر"
        verbose_name_plural = "استخرها"

    def __str__(self):
        return f"{self.name} - {self.get_gender_display()}"


class CreateClass(models.Model):
    STATUS_CLASSES_PUBLIC = 'public'
    STATUS_CLASSES_MIDPRIV = 'mid'
    STATUS = (
        (STATUS_CLASSES_PUBLIC, 'عمومی'),
        (STATUS_CLASSES_MIDPRIV, 'نیمه خصوصی')
    )

    course_code = models.IntegerField(unique=True, blank=True, null=True, verbose_name="کد کلاس")
    STATUS_CUSTOMUSER_FEMALE = 'female'
    STATUS_CUSTOMUSER_MALE = 'male'

    GENDER = (
        (STATUS_CUSTOMUSER_FEMALE, 'زنانه'),
        (STATUS_CUSTOMUSER_MALE, 'مردانه')
    )

    gender = models.CharField(choices=GENDER, max_length=10, null=True, blank=True, verbose_name="جنسیت کلاس")
    status = models.CharField(choices=STATUS, max_length=10, verbose_name="نوع کلاس")
    pool = models.ForeignKey(
        Pool, limit_choices_to={'status': 'education'}, on_delete=models.PROTECT,
        related_name='pool_course', blank=True, null=True, verbose_name="استخر"
    )

    class Meta:
        verbose_name = "کد کلاس"
        verbose_name_plural = "کد کلاس ها"

    def __str__(self):
        return str(self.course_code)

    @property
    def set_gender_course(self):
        self.gender = self.pool.gender
        return self.gender

    def save(self, *args, **kwargs):
        if self.pool and self.gender != self.pool.gender:
            raise ValidationError('جنسیت کلاس و استخر باید یکسان باشد.')

        if not self.course_code:
            while True:
                code = f'{random.randint(0, 9999):04}'
                if not CreateClass.objects.filter(course_code=code).exists():
                    self.course_code = int(code)
                    break
        super().save(*args, **kwargs)


# -----------------------------------------------------------------------------------------------------------------------

class Classes(models.Model):
    course_start = models.ForeignKey(
        CreateClass, on_delete=models.PROTECT, related_name='course_start',
        null=True, blank=True, verbose_name="کد دوره"
    )
    teacher = models.ForeignKey(
        CustomUser, on_delete=models.PROTECT, limit_choices_to={'status': 'teacher'},
        related_name='teacher_classes', verbose_name="مربی"
    )
    start = jmodels.jDateField(null=True, verbose_name="تاریخ شروع")
    end = jmodels.jDateField(null=True, blank=True, verbose_name="تاریخ پایان")
    start_clock = models.TimeField(verbose_name="ساعت شروع")
    end_clock = models.TimeField(verbose_name="ساعت پایان")
    active = models.BooleanField(default=False, verbose_name="فعال")
    price = models.PositiveBigIntegerField(verbose_name="قیمت")
    discount = models.PositiveIntegerField(blank=True, null=True, verbose_name="درصد تخفیف")
    total_price = models.PositiveBigIntegerField(blank=True, verbose_name="قیمت نهایی")

    class Meta:
        verbose_name = "کلاس"
        verbose_name_plural = "کلاس‌ها"

    @property
    def total_price(self):
        if self.discount:
            discount_amount = self.price * self.discount / 100
            return round(self.price - discount_amount)
        return self.price

    def __str__(self):
        return str(self.course_start)


# ------------------------------------------------------------------------------------------------------------------

class StartClass(models.Model):
    course = models.OneToOneField(
        Classes, on_delete=models.PROTECT, related_name='course',
        primary_key=True, verbose_name="دوره",

    )
    student = models.ManyToManyField(
        CustomUser, limit_choices_to={'status': 'student'},
        related_name='class_student', blank=True, verbose_name="دانش‌آموزان"
    )
    limit_register = models.PositiveIntegerField(default=3, verbose_name="حد ثبت‌نام")
    register_count = models.PositiveIntegerField(default=0, verbose_name="تعداد ثبت‌نام‌شده‌ها")

    def save(self, *args, **kwargs):
        status_limits = {
            CreateClass.STATUS_CLASSES_PUBLIC: 15,
            CreateClass.STATUS_CLASSES_MIDPRIV: 8,
        }
        status_class = self.course.course_start.status
        self.limit_register = status_limits.get(status_class, 3)  # مقدار پیش‌فرض ۳
        super().save(*args, **kwargs)

    def __str__(self):
        return f"شروع کلاس: {self.course}"

    class Meta:
        verbose_name = "شروع کلاس"
        verbose_name_plural = "شروع کلاس‌ها"


def validate_student_gender(sender, instance, action, pk_set, **kwargs):
    if action == 'pre_add':

        class_gender = instance.course.course_start.gender

        students = {s.id: s for s in CustomUser.objects.filter(id__in=pk_set)}
        for student_id in pk_set:
            student = students[student_id]
            if student.gender != class_gender:
                raise ValidationError(f"دانش‌آموز {student.username} با جنسیت کلاس مطابقت ندارد.")


m2m_changed.connect(validate_student_gender, sender=StartClass.student.through)


def create_start_class(sender, instance, created, **kwargs):
    if created:
        start_class = StartClass(course=instance)
        start_class.save()


post_save.connect(create_start_class, sender=Classes)


def update_register_count(sender, instance, action, pk_set, **kwargs):
    if action in ['post_add', 'post_remove', 'post_clear']:
        new_count = instance.student.count()  # تعداد جدید دانش‌آموزان
        if instance.register_count != new_count:  # اگر مقدار تغییر نکرده، ذخیره نکنیم
            instance.register_count = new_count
            instance.save(update_fields=['register_count'])  # فقط این فیلد را ذخیره کن


m2m_changed.connect(update_register_count, sender=StartClass.student.through)


# ---------------------------------------------------------------------------------------------------------


class RequestPrivateClass(models.Model):
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name='user_private',
        limit_choices_to=Q(status__in=[CustomUser.STATUS_CUSTOMUSER_DEFAULT,
                                       CustomUser.STATUS_CUSTOMUSER_STUDENT]) | Q(status__isnull=True),
        verbose_name="کاربر درخواست‌دهنده"
    )
    teacher = models.ForeignKey(
        CustomUser, blank=True, null=True, on_delete=models.CASCADE,
        limit_choices_to={'status': 'teacher'}, related_name='teacher_private',
        verbose_name="مربی"
    )
    pool = models.ForeignKey(
        Pool, blank=True, null=True, on_delete=models.CASCADE,
        related_name='pool_private', verbose_name="استخر"
    )
    person = models.PositiveSmallIntegerField(default=1, verbose_name="تعداد افراد")
    massage = models.TextField(verbose_name="پیام")
    acceptation = models.BooleanField(blank=True, null=True, verbose_name="تأیید شده")

    def __str__(self):
        return f"درخواست خصوصی - {self.user.last_name}"

    class Meta:
        verbose_name = "درخواست کلاس خصوصی"
        verbose_name_plural = "درخواست‌های کلاس خصوصی"


# ----------------------------------------------------------------------------------------------------------------------

class PrivateClass(models.Model):
    class_requested = models.ForeignKey(
        RequestPrivateClass, on_delete=models.CASCADE,
        related_name='class_requested',
        limit_choices_to={'acceptation': True},
        verbose_name="درخواست کلاس"
    )
    teacher = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        limit_choices_to={'status': 'teacher'},
        related_name='private_class_teacher',
        blank=True, null=True,
        verbose_name="مربی"
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='private_student',
        blank=True, null=True,
        limit_choices_to=~Q(status=CustomUser.STATUS_CUSTOMUSER_TEACHER),
        verbose_name="هنرجو"
    )
    start_date = jmodels.jDateField(verbose_name="تاریخ شروع")
    start_time = models.TimeField(verbose_name="ساعت شروع")
    price = models.PositiveBigIntegerField(verbose_name="قیمت")
    paid = models.BooleanField(default=False, verbose_name="پرداخت شده")

    def __str__(self):
        return f"کلاس خصوصی - {self.teacher.last_name} ({datetime2jalali(self.start_date).strftime('%Y/%m/%d')})"

    class Meta:
        verbose_name = "کلاس خصوصی"
        verbose_name_plural = "کلاس‌های خصوصی"


class Paid(models.Model):
    course = models.ForeignKey(
        Classes, on_delete=models.PROTECT,
        related_name='course_paid',
        blank=True, null=True,
        verbose_name="دوره"
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE,
        related_name='user_paid',
        verbose_name="کاربر"
    )
    price = models.BigIntegerField(verbose_name='مبلغ', default=0)
    paid = models.BooleanField(default=False, verbose_name="پرداخت شده")

    def __str__(self):
        return f"پرداخت {self.user.last_name}"

    def save(self, *args, **kwargs):
        if self.course and not self.price:
            self.price = self.course.total_price
        super().save(*args, **kwargs)

    class Meta:
        verbose_name = "پرداخت"
        verbose_name_plural = "پرداخت‌ها"


@receiver(post_save, sender=Paid)
def add_student_to_class(sender, instance, created, **kwargs):
    if instance.paid and instance.course:
        start_class = StartClass.objects.get(course=instance.course)
        start_class.student.add(instance.user)


class Coupon(models.Model):
    code = models.CharField(max_length=100, unique=True, verbose_name="کد تخفیف")
    active = models.BooleanField(default=False, verbose_name="فعال")
    start = jmodels.jDateTimeField(verbose_name="تاریخ شروع")
    end = jmodels.jDateTimeField(verbose_name="تاریخ پایان")
    discount = models.PositiveSmallIntegerField(verbose_name="درصد تخفیف")

    def __str__(self):
        return f"{self.code} - {self.discount}%"

    class Meta:
        verbose_name = "کد تخفیف"
        verbose_name_plural = "کدهای تخفیف"

# -----------------------------------------------------------------------------------------------------------------------
