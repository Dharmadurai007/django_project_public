#from django.db.models import fields
from rest_framework import serializers
from .models import Account, Destination

class DestinationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Destination
        fields = '__all__'

class AccountSerializer(serializers.ModelSerializer):
    destinations = DestinationSerializer(many=True, read_only=True)

    class Meta:
        model = Account
        fields = '__all__'


