from django.shortcuts import render
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ViewSet
from rest_framework.permissions import *
from rest_framework import status
from .serializers import *
from .permissions import *
from rest_framework.authtoken.models import Token
from django.contrib.auth import get_user_model, authenticate

# Create your views here.

User = get_user_model()








class TeacherSignUpViewSet(ModelViewSet):

    serializer_class = TeacherSignUpFormSerializer
    permission_classes = [IsSuperUser]
    queryset = TeacherSignUpForm.objects.all()

    @action(detail=True, methods=['post'])
    def accept(self, request, pk=None):
        signup_form = self.get_object()
        signup_form.accepted = True
        signup_form.save()
        return Response({'status': 'teacher accepted'}, status=status.HTTP_200_OK)





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
    http_method_names = ['get' , 'put']

    def get_queryset(self):
        return CustomUser.objects.filter(id=self.request.user.id)

    def perform_update(self, serializer):
        # به‌روزرسانی اطلاعات کاربر
        serializer.save()

    # def update(self, request, *args, **kwargs):
    #     partial = kwargs.pop('partial', False)
    #     instance = self.get_object()
    #     serializer = self.get_serializer(instance, data=request.data, partial=partial)
    #     serializer.is_valid(raise_exception=True)
    #     self.perform_update(serializer)
    #     return Response(serializer.data)
    #

class TeacherViewList(ModelViewSet):
    serializer_class = TeacherListSerializer
    permission_classes = [AllowAny]
    queryset = Teacher.objects.all()

    @action(detail=True, methods=['post'], url_path='rate')
    def rate_teacher(self, request, pk=None):
        teacher = self.get_object()
        user_id = request.data.get('user_id')
        rate = request.data.get('rate')

        if not user_id or not rate:
            return Response({"detail": "Invalid data"}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = CustomUser.objects.get(id=user_id)
        except CustomUser.DoesNotExist:
            return Response({"detail": "User not found"}, status=status.HTTP_404_NOT_FOUND)

        # Check if the user already rated this teacher
        rate_obj, created = RateToTeacher.objects.update_or_create(
            user=user,
            teacher=teacher,
            defaults={'rate': rate}
        )

        serializer = RateToTeacherSerializer(rate_obj)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
