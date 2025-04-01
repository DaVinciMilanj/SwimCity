from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db.models.signals import post_save, pre_save
from django.db.models import Avg
from django.contrib.auth.models import BaseUserManager
from django.dispatch import receiver
from django_jalali.db import models as jmodels


# Create your models here.


class CustomUserManager(BaseUserManager):
    def create_user(self, username, password=None, **extra_fields):
        if not username:
            raise ValueError('The Username must be set')
        user = self.model(username=username, **extra_fields)
        if password:  # Hash the password only if it's provided
            user.set_password(password)
        else:
            raise ValueError('Password must be provided.')
        user.save(using=self._db)
        return user

    def create_superuser(self, username, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(username, password, **extra_fields)


class CustomUser(AbstractUser):
    STATUS_CUSTOMUSER_DEFAULT = 'default'
    STATUS_CUSTOMUSER_TEACHER = 'teacher'
    STATUS_CUSTOMUSER_STUDENT = 'student'

    STATUS = (
        (STATUS_CUSTOMUSER_DEFAULT, 'کاربر عادی'),
        (STATUS_CUSTOMUSER_TEACHER, 'مربی'),
        (STATUS_CUSTOMUSER_STUDENT, 'هنرجو'),
    )

    STATUS_CUSTOMUSER_FEMALE = 'female'
    STATUS_CUSTOMUSER_MALE = 'male'

    GENDER = (
        (STATUS_CUSTOMUSER_FEMALE, 'زن'),
        (STATUS_CUSTOMUSER_MALE, 'مرد')
    )

    code_meli = models.CharField(max_length=15, unique=True, blank=True, null=True, verbose_name="کد ملی")
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True, verbose_name="شماره تلفن")
    birthday = jmodels.jDateField(blank=True, null=True, verbose_name="تاریخ تولد")
    status = models.CharField(choices=STATUS, max_length=20, blank=True, null=True, verbose_name="وضعیت کاربر")
    gender = models.CharField(choices=GENDER, max_length=10, blank=True, null=True, verbose_name="جنسیت")
    is_staff = models.BooleanField(default=False, verbose_name="مدیر سیستم")
    is_superuser = models.BooleanField(default=False, verbose_name="ابرکاربر")
    recovery_code = models.CharField(max_length=6, blank=True, null=True, verbose_name="کد بازیابی")
    image = models.ImageField(upload_to='profile', null=True, blank=True, verbose_name="تصویر پروفایل" , default='profile/default-avatar.jpg')

    objects = CustomUserManager()

    def __str__(self):
        return f"{self.first_name} {self.last_name}"

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربران"


class TeacherSignUpForm(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='teacher_form', verbose_name='کاربر')
    l_name = models.CharField(max_length=100, verbose_name='نام خانوادگی')
    phone_number = models.CharField(max_length=16, verbose_name='شماره تلفن')
    massage = models.TextField(verbose_name='پیام')
    accepted = models.BooleanField(default=False, verbose_name='تأیید شده')

    class Meta:
        verbose_name = 'فرم ثبت‌نام مربی'
        verbose_name_plural = 'فرم‌های ثبت‌نام مربیان'


@receiver(post_save, sender=TeacherSignUpForm)
def change_user_status_to_teacher(sender, instance, **kwargs):
    if instance.accepted:
        user = instance.user
        if user.status != CustomUser.STATUS_CUSTOMUSER_TEACHER:
            user.status = CustomUser.STATUS_CUSTOMUSER_TEACHER
            user.save()


class Teacher(models.Model):
    first_name = models.CharField(max_length=100, verbose_name='نام')
    last_name = models.CharField(max_length=100, verbose_name='نام خانوادگی')
    code_meli = models.CharField(max_length=15, verbose_name='کد ملی')
    phone = models.CharField(max_length=15, verbose_name='شماره تلفن')
    birthday = jmodels.jDateField(verbose_name='تاریخ تولد')
    image = models.ImageField(upload_to='teacher', blank=True, verbose_name='تصویر')
    active = models.BooleanField(default=True, verbose_name='فعال')
    average_rate = models.FloatField(default=0.0, verbose_name='امتیاز میانگین')

    def __str__(self):
        return self.last_name

    class Meta:
        verbose_name = 'مربی'
        verbose_name_plural = 'مربیان'


user_previous_status = {}


@receiver(pre_save, sender=CustomUser)
def get_previous_status(sender, instance, **kwargs):
    if instance.pk:
        previous_status = CustomUser.objects.get(pk=instance.pk).status
        user_previous_status[instance.pk] = previous_status
        print(f"Previous status saved: {previous_status}")  # Debugging


@receiver(post_save, sender=CustomUser)
def add_or_update_teacher(sender, instance, created, **kwargs):
    if instance.status == CustomUser.STATUS_CUSTOMUSER_TEACHER:
        if Teacher.objects.filter(phone=instance.phone).exists():
            # اگر معلمی با این شماره تلفن وجود دارد، اطلاعاتش را آپدیت کن
            Teacher.objects.filter(phone=instance.phone).update(
                first_name=instance.first_name,
                last_name=instance.last_name,
                code_meli=instance.code_meli,
                birthday=instance.birthday,
                image=instance.image
            )
        else:
            # اگر وجود نداشت، رکورد جدیدی بساز
            Teacher.objects.create(
                first_name=instance.first_name,
                last_name=instance.last_name,
                code_meli=instance.code_meli,
                phone=instance.phone,
                birthday=instance.birthday,
                image=instance.image
            )


class RateToTeacher(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, verbose_name='کاربر')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_rate', verbose_name='معلم')
    rate = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='امتیاز'
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'teacher'], name='unique_rate_per_user_teacher')
        ]
        verbose_name = 'امتیاز به  مربی'
        verbose_name_plural = 'امتیاز به مربیان'


@receiver(post_save, sender=RateToTeacher)
def update_teacher_average(sender, instance, **kwargs):
    teacher = instance.teacher
    avg = RateToTeacher.objects.filter(teacher=teacher).aggregate(avg=Avg('rate'))['avg'] or 0.0
    teacher.average_rate = round(avg, 1)
    teacher.save()


# ---------------------------------------------------------------------------------------------------------------------

class CommentTeacher(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='user_comment', verbose_name='نویسنده')
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_comment', verbose_name='مربی')
    comment = models.TextField(verbose_name='کامنت')
    create = jmodels.jDateTimeField(auto_now_add=True, verbose_name='ساخته شده')
    reply = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True, related_name='comment_reply',
                              verbose_name='ریپلای')
    is_reply = models.BooleanField(default=False, verbose_name='کامنت ریپلای')
    comment_report = models.ManyToManyField(CustomUser, blank=True, related_name='com_report',
                                            verbose_name='گزارش کامنت')
    total_comment_report = models.PositiveIntegerField(default=0, verbose_name='تعداد گزارشات')

    class Meta:
        verbose_name = "کامنت مربی"
        verbose_name_plural = "کامنت‌های مربیان"
        ordering = ['-total_comment_report']

    def __str__(self):
        return f"{self.user} → {self.teacher}: {self.comment[:30]}"

    def update_total_reports(self):
        self.total_comment_report = self.comment_report.count()
        self.save()

