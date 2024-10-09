from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from django_jalali.serializers.serializerfield import JDateField

from .models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'first_name', 'last_name', 'username', 'phone', 'gender', 'code_meli', 'birthday', 'status']


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
        fields = ['first_name', 'last_name', 'email', 'code_meli', 'birthday', 'gender']