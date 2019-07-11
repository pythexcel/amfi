from todo.models import AMC, Scheme, Nav, MFDownload, NavSerializer
from todo.serializers import UserSerializer, AMCSerializer, SchemeSerializer, MFDownloadSerializer

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

from rest_framework import status

from todo.util import get_date_index_data, fill_date_frame_data

# https://docs.djangoproject.com/en/2.0/topics/db/queries/#complex-lookups-with-q


@api_view()
def abs_return(request, amfi):
    scheme = Scheme.objects.get(fund_code=amfi)

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

    # try:

        return Response({
            "ytd": scheme.ytd_abs(),
            "oneyear": scheme.previous_yr_abs_today(1, 2),
            "threeyear": scheme.previous_yr_abs_today(3, 2),
            "2018-2019": scheme.previous_yr_abs(1),
            "2017-2018": scheme.previous_yr_abs(1, 1),
            "2016-2017": scheme.previous_yr_abs(1, 2),
            "2015-2016": scheme.previous_yr_abs(1, 3),
            "2014-2015": scheme.previous_yr_abs(1, 4)
        })
    # except Exception as e:
        # print '%s (%s)' % (e.message, type(e)):
        # return Response([], status.HTTP_500_INTERNAL_SERVER_ERROR)


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
