
from todo.models import AMC, Scheme, Nav, MFDownload
from todo.serializers import UserSerializer, AMCSerializer, SchemeSerializer, NavSerializer, MFDownloadSerializer

from rest_framework import viewsets

from rest_framework.views import APIView
from rest_framework.decorators import api_view
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


# https://docs.djangoproject.com/en/2.0/topics/db/queries/#complex-lookups-with-q


@api_view()
def fetch_nav(request, amfi):
    print(request.query_params["start_date"])
    start_date = datetime.datetime.strptime(
        request.query_params["start_date"], '%d-%m-%Y')
    end_date = datetime.datetime.strptime(
        request.query_params["end_date"], '%d-%m-%Y')

    scheme = Scheme.objects.get(fund_code=amfi)
    navs = Nav.objects.filter(scheme=scheme).filter(
        date__gt=start_date).exclude(date__lt=end_date)

    print(navs.query)
    ser = NavSerializer(navs, many=True)

    print(ser.data)

    df = pd.DataFrame(ser.data, columns=["nav", "date"])
    pt = pd.pivot_table(df, values="nav", index="date")
    print(pt)
    # print(pt.rolling(7))

    return Response(ser.data)


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
