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


@api_view()
def get_amcs(request):
    ret = AMC.objects.all()
    ser = AMCSerializer(ret, many=True)
    return Response(ser.data)


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
    schem = Scheme.objects.all()
    serial = SchemeSerializer(schem,many=True)
    return Response(serial.data)     


@api_view(['POST'])
def nav_last_update(request,scheme_id=None):
    nav = Nav.objects.filter(scheme=scheme_id)
    serializer = NavSerializer(nav,many=True) 
    return Response(serializer.data)

@api_view()
def schem_update_list(request):
    date = datetime.now() - timedelta(1)
    nav = Nav.objects.filter(date__gte=date)
    serializer = NavSerializer(nav,many=True) 
    unique_nav = []
    for data in serializer.data:
        if data['scheme'] not in unique_nav:
            unique_nav.append(data['scheme'])
        else:
            pass
    updated_schemes = []    
    for element in unique_nav:
        schem = Scheme.objects.get(id=element)
        ser = SchemeSerializer(schem,many=False)
        updated_schemes.append(ser.data['fund_name'])
    ret = ",".join(updated_schemes) 
    return Response(ret + " These are updated")   
    return Response(serializer.data)  

@api_view()
def nav_ten(request):
    date = datetime.now() - timedelta(10)
    nav = Nav.objects.filter(date__lte=date)
    serializer = NavSerializer(nav,many=True)
    unique_nav = []
    for data in serializer.data:
        if data['scheme'] not in unique_nav:
            unique_nav.append(data['scheme'])
        else:
            pass
    un_updated_schemes = []    
    for element in unique_nav:
        schem = Scheme.objects.get(id=element)
        ser = SchemeSerializer(schem,many=False)
        un_updated_schemes.append(ser.data['fund_name'])
    ret = ",".join(un_updated_schemes) 
    return Response(ret + " These are not updated from last ten days")   


    
