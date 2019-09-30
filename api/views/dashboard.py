from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import generics

from todo.jobs.health_check import nav_check as nav_check_data, index_check as index_check_data
from todo.jobs import schedule_daily_nav_download, process_nse_historial, process_bse_historial

from datetime import datetime,timedelta

import sys

from todo.logs import get_logs
from todo.models import AMC,Nav,Scheme,NavSerializer
from todo.serializers import AMCSerializer, SchemeSerializer
from django.core import serializers
from django.http import JsonResponse



@api_view()
def get_amcs(request):
    """
    
    Returns a list of all **Amc** in the system.
    
    """
    ret = AMC.objects.all()
    ser = AMCSerializer(ret, many=True)
    schemes_id = []
    for data in ser.data:
        if data not in schemes_id:
            schemes_id.append(data)
        else:
            pass   
    schemes = Scheme.objects.raw("SELECT 'a' as id, scheme_type, amc_id, COUNT(*) as cnt FROM todo_scheme group by scheme_type,amc_id ORDER by amc_id")

    print(schemes)

    amc_data = []
    for schem in schemes:
        amc_data.append({
            'Count' : getattr(schem,"cnt"),
            'Amc_id' : getattr(schem,"amc_id"),
            'Scheme_name' : getattr(schem,"scheme_type"),
        })

    for elem in ser.data:
        for data in amc_data:
            if data['Amc_id'] == elem['id']:
                elem[data['Scheme_name']] = data['Count']
               

    return Response ({
        "amc_data": ser.data
    })


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


@api_view()
def schem_list(request):
    """
    
    Returns a list of all **Schemes** in the system.
    
    """
    schem = Scheme.objects.all()
    serial = SchemeSerializer(schem,many=True)
    return Response(serial.data)     


@api_view()
def nav_last_update(request):
    """
    
    Returns a list of all **NAV/SCHEMES** in the system with a last updated date.
    
    """
    nav = nav_check_data(nav_type="latest_date") 
    return Response(nav)

@api_view()
def schem_update_list(request):
    """
    
    Returns a list of all **NAV/SCHEMES** in the system which are updated a day ago.
    
    """
    details = nav_check_data(nav_type="updated")
    return Response(details)

@api_view()
def nav_ten(request):
    """
    
    Returns a list of all **NAV/SCHEMES** in the system which are not updated for 10+ days.
    
    """
    details = nav_check_data(nav_type="un_updated")
    return Response(details)

    

    
