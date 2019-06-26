
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
import numpy as np
import requests
import datetime
from django.db.models import Q


# https://docs.djangoproject.com/en/2.0/topics/db/queries/#complex-lookups-with-q

@api_view()
def abs_return(request, amfi):
    scheme = Scheme.objects.get(fund_code=amfi)
    f = Q(scheme=scheme)

    start_date = False
    end_date = False

    if "start_date" in request.query_params:
        start_date = datetime.datetime.strptime(
            request.query_params["start_date"], '%d-%m-%Y')

    if "end_date" in request.query_params:
        end_date = datetime.datetime.strptime(
            request.query_params["end_date"], '%d-%m-%Y')
        f |= Q(date=end_date)

    if "timeframe" in request.query_params:
        if request.query_params["timeframe"] == "YTD":
            end_date = datetime.date.today()
            start_date = end_date - datetime.timedelta(days=365)

    if start_date:
        try:
            navs = Nav.objects.filter(scheme=scheme, date=start_date)
            print(navs.query)
            ser = NavSerializer(navs)
        except Nav.DoesNotExist:
            print(ser.data)

        start_date_delta_end = start_date - datetime.timedelta(days=2)
        start_date_delta_start = start_date + datetime.timedelta(days=2)
        f = Q(date__gt=start_date_delta_end) & Q(
            date__lt=start_date_delta_start)

    return Response([])
    
    if end_date:
        f &= Q(date__lt=end_date)

    navs = Nav.objects.filter(f)
    print(navs.query)
    ser = NavSerializer(navs, many=True)

    df = pd.DataFrame(ser.data, columns=["nav", "date"])

    start_date = df.iloc[0]["date"]
    end_date = df.iloc[len(df.index) - 1]["date"]

    idx = pd.date_range(start_date, end_date)

    df['Datetime'] = pd.to_datetime(df["date"])

    # print(df)
    df = df.set_index("Datetime")
    df = df.reindex(idx, method='ffill')
    # print(df)

    df = df.drop(['date'], axis=1)

    print(ser.data)
    return Response([])


@api_view()
def rolling_return(request, amfi):
    """
        rolling returns for different start end dates
        also different frequency
    """
    scheme = Scheme.objects.get(fund_code=amfi)

    f = Q(scheme=scheme)
    # navs = Nav.objects.filter(scheme=scheme)

    if "start_date" in request.query_params:
        start_date = datetime.datetime.strptime(
            request.query_params["start_date"], '%d-%m-%Y')
        # navs.filter(date__gt=start_date)
        f &= Q(date__gt=start_date)

    if "end_date" in request.query_params:
        end_date = datetime.datetime.strptime(
            request.query_params["end_date"], '%d-%m-%Y')
        # navs.filter(date__lt=end_date)
        f &= Q(date__lt=end_date)

    navs = Nav.objects.filter(f)
    print(navs.query)
    ser = NavSerializer(navs, many=True)

    # print(ser.data)

    df = pd.DataFrame(ser.data, columns=["nav", "date"])

    start_date = df.iloc[0]["date"]
    end_date = df.iloc[len(df.index) - 1]["date"]

    idx = pd.date_range(start_date, end_date)

    df['Datetime'] = pd.to_datetime(df["date"])

    # print(df)
    df = df.set_index("Datetime")
    df = df.reindex(idx, method='ffill')
    # print(df)

    df = df.drop(['date'], axis=1)

    # df['change'] = df['nav'].pct_change(periods=30)

    # //https://stackoverflow.com/questions/35339139/where-is-the-documentation-on-pandas-freq-tags

    if "freq" in request.query_params:
        df1 = df.asfreq(request.query_params["freq"])
    else:
        df1 = df.asfreq("M")
    # df[row["date"]-1]["nav"]
    #   if np.isnan(row["nav"]) else row["nav"]
    # df1.apply(lambda row:  print(row["date"]); row["nav"])

    df1['per'] = df1.pct_change()

    print(df1)

    return Response(df1.to_json(orient='index'))

    # pt = pd.pivot_table(df, values="nav", index="date")

    # df = pt.resample('1MIN').ffill()

    # print(df.head(10))
    # print(pt.rolling(7).pct_change())

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
