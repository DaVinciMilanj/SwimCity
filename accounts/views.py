import random
from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import *
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from Config import settings
from .serializers import *
from .permissions import *
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate
from kavenegar import *

# Create your views here.

User = get_user_model()


class SignUpViewSet(ModelViewSet):
    serializer_class = SignUpSerializer
    http_method_names = ['post']
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()  # کاربر جدید را ذخیره کنید
        return Response({
            "user": serializer.data,
            "message": "Registration successful"
        }, status=status.HTTP_201_CREATED)


class LoginViewSet(ViewSet):
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        info = serializer.validated_data['user']
        password = serializer.validated_data['password']

        try:
            if info.isdigit():
                user = CustomUser.objects.get(phone=info)
            else:
                user = CustomUser.objects.get(username=info)

        except CustomUser.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(request, username=user.username, password=password)

        if user is not None:
            # Clear existing token
            Token.objects.filter(user=user).delete()
            # Generate a new token
            token, created = Token.objects.get_or_create(user=user)
            return Response({
                'token': token.key,
                'is_superuser': user.is_superuser,
                'is_staff': user.is_staff
            }, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileCompleteSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser]

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        # به‌روزرسانی اطلاعات کاربر
        serializer.save()


class TeacherViewList(ModelViewSet):
    serializer_class = TeacherListSerializer
    permission_classes = [AllowAny]
    queryset = Teacher.objects.filter(active=True)

    # برای دریافت جزئیات معلم
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        user_rating = None

        # بررسی کنید که کاربر وارد شده است
        if request.user.is_authenticated:
            rating = RateToTeacher.objects.filter(teacher=instance, user=request.user).first()

            if rating:
                user_rating = rating.rate  # مقدار رأی فعلی کاربر
                print(f"Rating object: {rating}")

        # اضافه کردن رأی کاربر به داده‌های بازگشتی
        data = serializer.data
        data['user_rating'] = user_rating  # مقدار رأی یا None
        print(user_rating)
        return Response(data)

    @action(detail=True, methods=['post'], url_path='rate', url_name='rate_teacher',
            permission_classes=[IsAuthenticated])
    def rate_teacher(self, request, pk=None):
        teacher = self.get_object()
        user = request.user
        serializer = RateToTeacherSerializer(data=request.data, context={'request': request})

        if serializer.is_valid():
            # ایجاد یا به‌روزرسانی رأی
            RateToTeacher.objects.update_or_create(
                teacher=teacher,
                user=user,
                defaults={'rate': serializer.validated_data['rate']}
            )

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class TeacherSignUpViewSet(ModelViewSet):
    serializer_class = TeacherSignUpFormSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class ForgotPasswordViewSet(ViewSet):
    @action(detail=False, methods=['post'], url_path='send-recovery-code')
    def send_recovery_code(self, request):
        phone = request.data.get('phone')

        # بررسی وجود کاربر
        try:
            user = User.objects.get(phone=phone)
        except User.DoesNotExist:
            return Response({'error': 'User with this phone number does not exist.'}, status=status.HTTP_404_NOT_FOUND)

        # تولید کد بازیابی
        recovery_code = random.randint(100000, 999999)
        user.recovery_code = recovery_code  # ذخیره در فیلد مرتبط
        user.save()

        # ارسال پیامک
        try:
            api = KavenegarAPI(settings.KAVENEGAR_API_KEY)
            params = {
                'sender': '2000660110',
                'receptor': phone,
                'message': f'کد بازیابی شما: {recovery_code}',
            }
            api.sms_send(params)
        except (APIException, HTTPException) as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        return Response({'message': 'Recovery code sent successfully.'}, status=status.HTTP_200_OK)
