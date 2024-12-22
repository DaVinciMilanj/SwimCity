from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django_jalali.serializers.serializerfield import JDateField
from jdatetime import date as jdate
from .models import *


class SignUpSerializer(serializers.ModelSerializer):
    username = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    phone = serializers.CharField(
        required=True,
        validators=[UniqueValidator(queryset=CustomUser.objects.all())]
    )
    password = serializers.CharField(
        write_only=True,
        required=True,
        validators=[validate_password],
        style={'input_type': 'password'}
    )
    password2 = serializers.CharField(
        write_only=True,
        required=True,
        style={'input_type': 'password'}
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'phone', 'password', 'password2')

    def validate(self, attrs):
        if attrs['password'] != attrs['password2']:
            raise serializers.ValidationError({"password": "Passwords don't match."})
        return attrs

    def create(self, validated_data):
        user = CustomUser.objects.create(
            username=validated_data['username'],
            phone=validated_data['phone'],
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


class LoginSerializer(serializers.Serializer):
    user = serializers.CharField()
    password = serializers.CharField(write_only=True)


class ProfileCompleteSerializer(serializers.ModelSerializer):
    birthday = JDateField(
        required=True,
        format='%Y-%m-%d',  # فرمت تاریخ جلالی به شکل سال-ماه-روز
        input_formats=['%Y-%m-%d']  # فرمت ورودی برای تاریخ جلالی
    )

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'phone', 'code_meli', 'first_name', 'last_name', 'email', 'birthday', 'gender',
                  'image']
        read_only_fields = ['username']


class TeacherListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Teacher
        fields = ['id', 'first_name', 'last_name', 'code_meli', 'phone', 'birthday', 'image', 'active', 'average_rate']


class GetUserRateSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateToTeacher
        fields = ['user', 'teacher', 'rate']


class RateToTeacherSerializer(serializers.ModelSerializer):
    class Meta:
        model = RateToTeacher
        fields = ['rate']
        extra_kwargs = {
            'rate': {'required': True},
        }

    def validate_rate(self, value):
        if value < 1 or value > 5:
            raise serializers.ValidationError("Rate must be between 1 and 5.")
        return value

    def create(self, validated_data):
        request = self.context.get('request')
        if request and hasattr(request, 'user'):
            validated_data['user'] = request.user
        return super().create(validated_data)



class TeacherSignUpFormSerializer(serializers.ModelSerializer):
    class Meta:
        model = TeacherSignUpForm
        fields = ['l_name', 'phone_number', 'massage']

