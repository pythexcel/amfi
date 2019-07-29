from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import generics

from todo.jobs.health_check import nav_check as nav_check_data, index_check as index_check_data
from todo.jobs import schedule_daily_nav_download, process_nse_historial, process_bse_historial

import datetime

import sys

from todo.logs import get_logs


@api_view()
def nav_check(request):
    return Response(nav_check_data())


@api_view()
def nav_run_script(request):
    schedule_daily_nav_download.modify(next_run_time=datetime.datetime.now())
    return Response([])


@api_view()
def get_process_logs(request):
    get_logs(request.process_name)
    return Response([])


@api_view()
def index_check(request):
    return Response(index_check_data())


@api_view()
def index_run_script(request):
    process_nse_historial.modify(next_run_time=datetime.datetime.now())
    process_bse_historial.modify(next_run_time=datetime.datetime.now())
    return Response([])
