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
        (STATUS_CUSTOMUSER_DEFAULT, 'default'),
        (STATUS_CUSTOMUSER_TEACHER, 'teacher'),
        (STATUS_CUSTOMUSER_STUDENT, 'student'),
    )

    STATUS_CUSTOMUSER_FEMALE = 'female'
    STATUS_CUSTOMUSER_MALE = 'male'

    GENDER = (
        (STATUS_CUSTOMUSER_FEMALE, 'دختر'),
        (STATUS_CUSTOMUSER_MALE, 'پسر')
    )

    code_meli = models.CharField(max_length=15, unique=True, blank=True, null=True)
    phone = models.CharField(max_length=15, unique=True, blank=True, null=True)
    birthday = jmodels.jDateField(blank=True, null=True)
    status = models.CharField(choices=STATUS, max_length=20, blank=True, null=True)
    gender = models.CharField(choices=GENDER, max_length=10, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    recovery_code = models.CharField(max_length=6, blank=True, null=True)
    image = models.ImageField(upload_to='profile', null=True, blank=True)

    objects = CustomUserManager()

    def __str__(self):
        return self.last_name


class TeacherSignUpForm(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='teacher_form')
    l_name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=16)
    massage = models.TextField()
    accepted = models.BooleanField( default=False )


@receiver(post_save, sender=TeacherSignUpForm)
def change_user_status_to_teacher(sender, instance, **kwargs):
    if instance.accepted:
        user = instance.user
        if user.status != CustomUser.STATUS_CUSTOMUSER_TEACHER:
            user.status = CustomUser.STATUS_CUSTOMUSER_TEACHER
            user.save()


class Teacher(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    code_meli = models.CharField(max_length=15)
    phone = models.CharField(max_length=15)
    birthday = jmodels.jDateField()
    image = models.ImageField(upload_to='teacher', blank=True)
    active = models.BooleanField(default=True)
    average_rate = models.FloatField(default=0.0)  # New field

    def __str__(self):
        return self.last_name


user_previous_status = {}


@receiver(pre_save, sender=CustomUser)
def get_previous_status(sender, instance, **kwargs):
    if instance.pk:
        previous_status = CustomUser.objects.get(pk=instance.pk).status
        user_previous_status[instance.pk] = previous_status
        print(f"Previous status saved: {previous_status}")  # Debugging


@receiver(post_save, sender=CustomUser)
def add_or_update_teacher(sender, instance, created, **kwargs):
    print(f"Post-save signal triggered for user: {instance}")  # Debugging
    if created and instance.status == CustomUser.STATUS_CUSTOMUSER_TEACHER:
        print("Creating teacher record...")
        Teacher.objects.create(
            first_name=instance.first_name,
            last_name=instance.last_name,
            code_meli=instance.code_meli,
            phone=instance.phone,
            birthday=instance.birthday,
            image=instance.image
        )
    if not created:
        previous_status = user_previous_status.get(instance.pk)
        if instance.status == CustomUser.STATUS_CUSTOMUSER_TEACHER:
            print("Updating teacher record...")
            Teacher.objects.update_or_create(
                code_meli=instance.code_meli,
                defaults={
                    "first_name": instance.first_name,
                    "last_name": instance.last_name,
                    "phone": instance.phone,
                    "birthday": instance.birthday,
                    "image": instance.image
                }
            )


class RateToTeacher(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    teacher = models.ForeignKey(Teacher, on_delete=models.CASCADE, related_name='teacher_rate')
    rate = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['user', 'teacher'], name='unique_rate_per_user_teacher')
        ]


@receiver(post_save, sender=RateToTeacher)
def update_teacher_average(sender, instance, **kwargs):
    teacher = instance.teacher
    avg = RateToTeacher.objects.filter(teacher=teacher).aggregate(avg=Avg('rate'))['avg'] or 0.0
    teacher.average_rate = round(avg, 1)
    teacher.save()


