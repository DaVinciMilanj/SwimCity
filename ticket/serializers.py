from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from .models import *
from pool.serializers import PoolsSerializer
from django_jalali.serializers.serializerfield import JDateField


class PoolTicketSerializer(serializers.ModelSerializer):
    final_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = PoolTicket
        fields = ['id', 'pool', 'description', 'price', 'discount_amount', 'final_price']


class TicketReservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = TicketReservation
        fields = ['id','ticket' ,'full_name', 'phone_number', 'quantity']


class PaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = ['id', 'reservation', 'paid', 'ref_id', 'price', 'authority', 'paid']



