from todo.models import AMC, Scheme, Nav, MFDownload
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission


class AMCSerializer(serializers.ModelSerializer):
    class Meta:
        model = AMC
        fields = '__all__'


class SchemeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scheme
        fields = '__all__'


class NavSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nav
        fields = '__all__'


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = '__all__'


class PermSerializer(serializers.ModelSerializer):
    class Meta:
        model = Permission
        fields = '__all__'


class MFDownloadSerializer(serializers.ModelSerializer):
    class Meta:
        model = MFDownload
        fields = '__all__'
