from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import generics

from todo.jobs.health_check import nav_check as nav_check_data, index_check as index_check_data
from todo.jobs import schedule_daily_nav_download, process_nse_historial, process_bse_historial

#from datetime import datetime,timedelta
from dateutil.relativedelta import relativedelta
import sys
import datetime
from todo.logs import get_logs
from todo.models import AMC,Nav,Scheme,NavSerializer
from todo.models import Index_scheme_mapping
from todo.serializers import AMCSerializer, SchemeSerializer
from django.core import serializers
from django.http import JsonResponse
from todo.tests import yearly_amc_return,yearly_ter_return


#Api for return scheme and index info// send payload in request

@api_view(['POST'])
def get_abs_value(request):
    start_date = request.data.get("start_date")
    end_date = request.data.get("end_date")
    fund_code = request.data.get("fund_code")
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
    fun_return = Index_scheme_mapping(start_date,end_date,fund_code)  
    return Response(fun_return)



@api_view(['POST'])
def get_yearly_amc_amount(request):
    start_date = request.data.get("start_date")
    fund_code = request.data.get("fund_code")
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = start_date + datetime.timedelta(days=365*1)
    fun_return = yearly_amc_return(start_date,end_date,fund_code)  
    return Response(fun_return)


@api_view(['POST'])
def get_yearly_ter(request):
    start_date = request.data.get("start_date")
    fund_code = request.data.get("fund_code")
    start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
    end_date = start_date + datetime.timedelta(days=365*1)
    fun_return = yearly_ter_return(start_date,end_date,fund_code)  
    return Response(fun_return)




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
    schemes = Scheme.objects.raw("SELECT a.id as amc_id, a.*, s.* FROM todo_amc as a left JOIN todo_scheme as s on a.id = s.amc_id")        
    amc = Scheme.objects.raw("SELECT id  FROM todo_amc  group by id order by id")
    amc_data = []
    result = []
    for schem in amc: 
        amc_data.append({
            "id" : getattr(schem,"id")
        })
    for item in amc_data:
        am_data = {
            'amc_id' : item['id']
        }
        schemes_data = []
        for sch in schemes:
            amc_id = getattr(sch,"amc_id")
            if (amc_id == item['id']):
                schemes_data.append({
                    "id":getattr(sch,"id"),
                    "scheme_category":getattr(sch,"scheme_category"),
                    "scheme_type":getattr(sch,"scheme_type"),
                    "scheme_sub_type":getattr(sch,"scheme_sub_type"),
                    "fund_code":getattr(sch,"fund_code"),
                    "fund_name":getattr(sch,"fund_name"),
                    "fund_option":getattr(sch,"fund_option"),
                    "fund_type":getattr(sch,"fund_type"),
                    "fund_active":getattr(sch,"fund_active"),
                    "line":getattr(sch,"line")
                })
                am_data['name'] = getattr(sch,"name")
                am_data['amc_no'] = getattr(sch,'amc_no')
                am_data['parsed'] = getattr(sch,'parsed')
                am_data['next_amc_no'] = getattr(sch,'next_amc_no')
                am_data['logo'] = getattr(sch,'logo')
        am_data["schemes"] = schemes_data
        result.append(am_data)
    return Response (result)


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

    

    
