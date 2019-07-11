from todo.models import AMC, Scheme, Nav, MFDownload
from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth.models import Permission


class AMCSerializer(serializers.ModelSerializer):
    class Meta:
        model = AMC
        fields = '__all__'


class SchemeSerializer(serializers.ModelSerializer):
    clean_name = serializers.SerializerMethodField()
    class Meta:
        model = Scheme
        fields = '__all__'

    def get_clean_name(self, obj):
        return obj.get_clean_name()

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
