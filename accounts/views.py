from django.shortcuts import render
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



class SignUpViewSet(ModelViewSet):
    serializer_class = SignUpSerializer
    http_method_names = ['post']
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_201_CREATED)




class LoginViewSet(ViewSet):
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        info = serializer.validated_data['user']
        password = serializer.validated_data['password']

        try:
            if info.isdigit():
                user = User.objects.get(phone=info)
            else:
                user = User.objects.get(username=info)

        except User.DoesNotExist:
            return Response(status=status.HTTP_401_UNAUTHORIZED)

        user = authenticate(request, username=user.username, password=password)

        if user is not None:
            token, created = Token.objects.get_or_create(user=user)
            return Response({'token': token.key}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)


class ProfileViewSet(ModelViewSet):
    serializer_class = ProfileCompleteSerializer
    permission_classes = [IsAuthenticated] 

    def get_queryset(self):

        return CustomUser.objects.filter(id=self.request.user.id)

    def perform_update(self, serializer):

        serializer.save(user=self.request.user)