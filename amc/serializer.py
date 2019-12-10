from amc.models import Scheme_Name_Mismatch,Scheme_AUM,Scheme_TER
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission


class Scheme_Name_Mismatch_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Scheme_Name_Mismatch
        fields = '__all__'


class Scheme_AUM_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Scheme_AUM
        fields = '__all__'
        

class Scheme_TER_Serializer(serializers.ModelSerializer):
    class Meta:
        model = Scheme_TER
        fields = '__all__'
