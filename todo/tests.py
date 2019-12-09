from django.test import TestCase
from todo.models import Scheme_Info,SchemeinfoSerializer,Index,IndexSerializer,IndexData,Scheme,SchemeSerializer
import todo.util
from math import ceil
import numpy as np
from todo.util import maping_dict
from django.db.models import Q
from amc.models import Scheme_AUM
from amc.serializer import Scheme_AUM_Serializer


def Index_scheme_mapping(start_date,end_date,scheme_id):
    ret = Scheme_Info.objects.filter(scheme_id=scheme_id)
    scheme_seri = SchemeinfoSerializer(ret,many=True)
    scheme_name = scheme_seri.data
    if scheme_name:
        scheme_name = scheme_name[0]
        benchmark = scheme_name['benchmark']
        stopwords = ['Total','Return','Index','TRI','(',')','-','Net']
        querywords = benchmark.split()
        resultwords  = [word for word in querywords if word not in stopwords]
        result = ' '.join(resultwords)
        for record in maping_dict:
            benchmark_name = record['benchmark_name']
            benchmark = record['benchmark']
            if benchmark_name == result:
                print("fund_benchmark",benchmark_name)
                print("result",result)
                print("matechedddddddddddddddddddddddddddddddddddddd")
                fund_benchmark = benchmark
                abs_details = benchmark_abs_details(start_date,end_date,fund_benchmark,scheme_id)
                print("abs_details",abs_details)
                return abs_details
            else:
                pass
    else:
        return None

# Create your tests here.
def benchmark_abs_details(start_date,end_date,fund_benchmark,scheme_id):
    ret = Index.objects.filter(name=fund_benchmark)
    seri = IndexSerializer(ret,many=True)
    Index_details = seri.data
    if Index_details:
        Index_details = Index_details[0]
        index = Index_details['id']
        start_nav = IndexData.get_price_for_date(index,start_date)
        end_nav = IndexData.get_price_for_date(index,end_date)
        print("end_nav",end_nav,"start_nav",start_nav)
        pct = (end_nav - start_nav) / (start_nav)
        if np.isnan(pct) == False:
            abs_ptc = todo.util.float_round(pct*100, 2, ceil)
            return abs_ptc
    else:
        print("benchmark not in index")
        return None


        
def yearly_amc_return(start_date,end_date,fund_code):
    ret = Scheme.objects.filter(fund_code=fund_code)
    serial = SchemeSerializer(ret,many=True)
    scheme_data = serial.data
    if scheme_data:
        scheme_data = scheme_data[0]
        fund_name = scheme_data['fund_name']
        scheme_id = scheme_data['id']
        filter_data = Q(date__gte=start_date) & Q(
                date__lte=end_date) & Q(scheme_id=scheme_id)
        output = Scheme_AUM.objects.filter(filter_data).order_by('-date')
        if output.count() > 0:
            scheme_seri = Scheme_AUM_Serializer(output,many=True)
            scheme_name = scheme_seri.data
            return scheme_name
        else:
            return "No data available for given data"
    else:
        return "No scheme available for given fundcode"
