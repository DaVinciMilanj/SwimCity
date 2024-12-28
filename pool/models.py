from decimal import Decimal

from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.exceptions import ValidationError
from django_jalali.db import models as jmodels
from accounts.models import CustomUser
# Create your models here.
import random


# Create your models here.

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
        (STATUS_CUSTOMUSER_FEMALE, 'دختر'),
        (STATUS_CUSTOMUSER_MALE, 'پسر')
    )
    gender = models.CharField(choices=GENDER, max_length=10, null=True, blank=True)
    image = models.ImageField(upload_to='pool_images/', null=True, blank=True)
    name = models.CharField(max_length=50)
    active = models.BooleanField(default=True)
    address = models.TextField()
    status = models.CharField(choices=STATUS, max_length=20, blank=True, null=True)

    def __str__(self):
        return self.name


class CreateClass(models.Model):
    STATUS_CLASSES_PRIVATE = 'private'
    STATUS_CLASSES_PUBLIC = 'public'
    STATUS_CLASSES_MIDPRIV = 'mid'
    STATUS = (
        (STATUS_CLASSES_PRIVATE, 'خصوصی'),
        (STATUS_CLASSES_PUBLIC, 'عمومی'),
        (STATUS_CLASSES_MIDPRIV, 'نیمه خصوصی')
    )
    course_code = models.IntegerField(unique=True, blank=True, null=True)

    STATUS_CUSTOMUSER_FEMALE = 'female'
    STATUS_CUSTOMUSER_MALE = 'male'

    GENDER = (
        (STATUS_CUSTOMUSER_FEMALE, 'دختر'),
        (STATUS_CUSTOMUSER_MALE, 'پسر')
    )
    gender = models.CharField(choices=GENDER, max_length=10, null=True, blank=True)

    status = models.CharField(choices=STATUS, max_length=10)
    pool = models.ForeignKey(Pool, limit_choices_to={'status': 'education'}, on_delete=models.PROTECT,
                             related_name='pool_course', blank=True, null=True)

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
                    self.course_code = code
                    break
        super().save(*args, **kwargs)


class Classes(models.Model):
    course_start = models.ForeignKey(CreateClass, on_delete=models.PROTECT, related_name='course_start', null=True,
                                     blank=True)
    teacher = models.ForeignKey(CustomUser, on_delete=models.PROTECT, limit_choices_to={'status': 'teacher'}
                                , related_name='teacher_classes')
    start = jmodels.jDateField(null=True)
    end = jmodels.jDateField(blank=True)
    start_clock = models.TimeField()
    end_clock = models.TimeField()
    active = models.BooleanField(default=False)
    price = models.PositiveBigIntegerField()
    discount = models.PositiveIntegerField(blank=True, null=True)
    total_price = models.PositiveBigIntegerField(blank=True)

    @property
    def total_price(self):
        if self.discount:
            discount_amount = self.price * self.discount / 100
            return round(self.price - discount_amount)
        return self.price

    def __str__(self):
        return str(self.course_start)


class StartClass(models.Model):
    course = models.OneToOneField(Classes, on_delete=models.PROTECT, related_name='course', primary_key=True)
    student = models.ManyToManyField(CustomUser, limit_choices_to={'status': 'student'},
                                     related_name='class_student', blank=True)
    limit_register = models.PositiveIntegerField(default=3)
    register_count = models.PositiveIntegerField(default=0)

    def update_register_count(self):
        """به‌روزرسانی تعداد ثبت‌نام‌ها بر اساس تعداد دانش‌آموزان"""
        self.register_count = self.student.count()
        # از update_fields استفاده کنید تا فقط فیلد register_count ذخیره شود
        self.save(update_fields=['register_count'])

    def clean(self):
        # بررسی تعداد ثبت‌نام‌ها
        current_count = self.register_count
        if current_count >= self.limit_register:
            raise ValidationError(f"تعداد ثبت‌نام‌ها نمی‌تواند بیشتر از {self.limit_register} باشد.")

    def save(self, *args, **kwargs):
        # بررسی جنسیت برای ثبت نام
        gender = self.course.course_start.gender
        for student in self.student.all():
            if student.gender != gender:
                raise ValidationError('جنسیت دانش‌آموز با جنسیت کلاس مطابقت ندارد.')


        super().save(*args, **kwargs)




def create_start_class(sender, instance, created, **kwargs):
    if created:
        start_class = StartClass(course=instance)
        start_class.save()


post_save.connect(create_start_class , sender=Classes)









class Paid(models.Model):
    course = models.ForeignKey(Classes, on_delete=models.CASCADE, related_name='course_paid')
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_paid')
    paid = models.BooleanField(default=False)

    def __str__(self):
        return self.user.last_name

    def enroll_in_class(self):
        if self.paid:

            try:
                start_class = StartClass.objects.get(course=self.course)
            except StartClass.DoesNotExist:
                raise ValueError("Class not found for this course.")

            if start_class.register_count < start_class.limit_register:

                start_class.student.add(self.user)

                start_class.register_count += 1
                start_class.save()

                self.user.status = CustomUser.STATUS_CUSTOMUSER_STUDENT
                self.user.save()
            else:
                raise ValueError("Class is full. No more students can be added.")
