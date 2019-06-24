
from todo.models import AMC, Scheme, Nav, MFDownload
from todo.serializers import UserSerializer, AMCSerializer, SchemeSerializer, NavSerializer, MFDownloadSerializer

from rest_framework import viewsets

from rest_framework.views import APIView
from rest_framework.response import Response

from django.contrib.auth import authenticate
from rest_framework import status

from django.contrib.auth.models import User
from rest_framework.authtoken.models import Token

from rest_framework.permissions import IsAuthenticated, AllowAny, DjangoModelPermissions

import quandl
import pandas as pd
import requests
import datetime


"""
FULL CRUD OPERATION FOR TODO
"""


# class TodoViewSet(viewsets.ModelViewSet):
#     serializer_class = TodoSerializer
#     queryset = Todo.objects.all()
#     permission_classes = (DjangoModelPermissions,)


class UserAuth(APIView):
    """
    Manager User Login and other things
    """

    permission_classes = (AllowAny,)

    def get(self, request):

        # quandl.ApiConfig.api_key = 'NNVGCuqZtoU22g-RBVU6'

        # data = quandl.get('AMFI/140249', start_date='2018-01-01', end_date='2019-01-01')

        # data = pd.DataFrame(data)

        # print(data)

        # data = data.loc[:,['Net Asset Value']]

        # print(data.rolling(30))

        # return Response([])

        # amc_id = [1, 27]
        

        print(start)
        print(end)

        return Response([])

    permission_classes = (AllowAny,)

    def post(self, request):
        """
        login
        """
        quandl.ApiConfig.api_key = 'NNVGCuqZtoU22g-RBVU6'

        data = quandl.get(
            'AMFI/140249', start_date='2019-01-01', end_date='2019-06-21')

        x = pd.DataFrame(data)

        print(x)

        return Response([])

        # user = authenticate(username=request.data.get(
        #     "username"), password=request.data.get("password"))
        # if user is not None:
        #     # A backend authenticated the credentials
        #     try:
        #         token = Token.objects.get(user_id=user.id)
        #     except Token.DoesNotExist:
        #         token = Token.objects.create(user=user)
        #     return Response(token.key)
        # else:
        #     # No backend authenticated the credentials
        #     return Response([], status=status.HTTP_401_UNAUTHORIZED)


class UserRegister(APIView):
    """
    Create user 
    """

    def post(self, request):
        user = User.objects.create_user(
            username=request.data.get("username"),
            email=request.data.get("email"),
            password=request.data.get("password"))
        user.save()

        if user is not None:
            token = Token.objects.create(user=user)
            print(token.key)
            print(user)
            return Response(token.key)
        else:
            return Response([], status=status.HTTP_400_BAD_REQUEST)
