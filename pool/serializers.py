from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django_jalali.serializers.serializerfield import JDateField
from accounts.serializers import *

from .models import *



class PoolsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Pool
        fields = ['id', 'name', 'address', 'status', 'gender' , 'image']


class CoursesSerializer(serializers.ModelSerializer):
    pool = serializers.CharField(source='course_start.pool', read_only=True)
    start = JDateField(
        required=True,
        format='%Y-%m-%d',  # فرمت تاریخ جلالی به شکل سال-ماه-روز
        input_formats=['%Y-%m-%d'])
    end = JDateField(
        required=True,
        format='%Y-%m-%d',  # فرمت تاریخ جلالی به شکل سال-ماه-روز
        input_formats=['%Y-%m-%d']
    )
    teacher = serializers.CharField(source='teacher.last_name', read_only=True)

    class Meta:
        model = Classes
        fields = ['id', 'pool', 'teacher', 'start', 'end', 'start_clock', 'end_clock', 'price', 'discount',
                  'total_price']


class PaidSerializer(serializers.ModelSerializer):
    price = serializers.IntegerField(source='course.total_price', read_only=True)

    class Meta:
        model = Paid
        fields = ['id', 'price', 'course', 'user']
