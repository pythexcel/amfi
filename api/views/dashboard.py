from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import generics

from todo.jobs.health_check import nav_check as nav_check_data
from todo.jobs import schedule_daily_nav_download

import datetime

import sys

@api_view()
def nav_check(request):
    return Response(nav_check_data())


@api_view()
def nav_run_script(request):
    sys.stdout = open('file.txt', 'w')
    schedule_daily_nav_download.modify(next_run_time=datetime.datetime.now())
    return Response([])
