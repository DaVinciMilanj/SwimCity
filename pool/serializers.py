from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django_jalali.serializers.serializerfield import JDateField
from accounts.serializers import *

from .models import *


class PoolsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pool
        fields = ['id', 'name', 'address', 'status', 'gender', 'image']


class CoursesSerializer(serializers.ModelSerializer):
    pool = serializers.CharField(source='course_start.pool', read_only=True)
    code = serializers.IntegerField(source='course_start.course_code', read_only=True)
    start = JDateField(
        required=True,
        format='%Y-%m-%d',  # فرمت تاریخ جلالی به شکل سال-ماه-روز
        input_formats=['%Y-%m-%d'])
    end = JDateField(
        required=True,
        format='%Y-%m-%d',  # فرمت تاریخ جلالی به شکل سال-ماه-روز
        input_formats=['%Y-%m-%d']
    )
    teacher = TeacherListSerializer()
    limit_register = serializers.IntegerField(source='course.limit_register', read_only=True)
    register_count = serializers.IntegerField(source='course.register_count', read_only=True)

    class Meta:
        model = Classes
        fields = ['id', 'pool', 'code','title','teacher', 'start', 'end', 'start_clock', 'end_clock', 'price', 'discount',
                  'total_price', 'limit_register', 'register_count']


class RequestPrivateClassSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)  # فقط خواندنی
    teacher = serializers.PrimaryKeyRelatedField(
        queryset=CustomUser.objects.filter(status='teacher'))  # فقط id را می‌گیرد
    pool = serializers.PrimaryKeyRelatedField(queryset=Pool.objects.all())  # فقط id را می‌گیرد

    class Meta:
        model = RequestPrivateClass
        fields = ['id', 'user', 'teacher', 'pool', 'person', 'massage', 'acceptation']


class RequestPrivateClassReadSerializer(serializers.ModelSerializer):
    pool = PoolsSerializer()
    user = GetUserSerializer()
    teacher = TeacherListSerializer()

    class Meta:
        model = RequestPrivateClass
        fields = ['id', 'user', 'teacher', 'pool', 'person', 'massage', 'acceptation']


class CreatePrivateClassSerializer(serializers.ModelSerializer):
    start_date = JDateField(
        required=True,
        format='%Y-%m-%d',  # فرمت تاریخ جلالی به شکل سال-ماه-روز
        input_formats=['%Y-%m-%d'])

    class Meta:
        model = PrivateClass
        fields = ['id', 'class_requested', 'teacher', 'user', 'start_date', 'start_time', 'price', 'paid']


class ShowPrivateClassSerializer(serializers.ModelSerializer):
    start_date = JDateField(
        required=True,
        format='%Y-%m-%d',  # فرمت تاریخ جلالی به شکل سال-ماه-روز
        input_formats=['%Y-%m-%d'])

    pool = serializers.CharField(source='class_requested.pool')
    teacher = TeacherListSerializer()
    user = GetUserSerializer()

    class Meta:
        model = PrivateClass
        fields = ['id', 'class_requested', 'pool', 'teacher', 'user', 'start_date', 'start_time', 'price', 'paid']


class PaidSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paid
        fields = ['id', 'price', 'course', 'user', 'ref_id', 'authority' , 'paid']


class MyCourseSerializer(serializers.ModelSerializer):
    course = CoursesSerializer()
    price = serializers.SerializerMethodField()

    class Meta:
        model = StartClass
        fields = ['course', 'price']

    def get_price(self, obj):
        paid_instance = Paid.objects.filter(course=obj.course, user=self.context['request'].user).first()
        return paid_instance.price if paid_instance else 0  # اگر پرداختی وجود نداشت، مقدار ۰ را برگرداند


class PaidPrivateClassSerializer(serializers.ModelSerializer):
    class Meta:
        model = Paid
        fields = ['id' ,'price','private_class','user', 'ref_id', 'authority' , 'paid' ]
