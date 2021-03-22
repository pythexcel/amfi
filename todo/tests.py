from django.test import TestCase
from todo.models import Scheme_Info,SchemeinfoSerializer,Index,IndexSerializer,IndexData
import todo.util
from math import ceil



def Index_scheme_mapping(start_date,end_date,scheme_id):
    ret = Scheme_Info.objects.filter(scheme_id=scheme_id)
    scheme_seri = SchemeinfoSerializer(ret,many=True)
    scheme_name = scheme_seri.data
    if scheme_name:
        scheme_name = scheme_name[0]
        benchmark = scheme_name['benchmark']
        stopwords = ['Total','Return','Index','TRI']
        querywords = benchmark.split()
        resultwords  = [word for word in querywords if word not in stopwords]
        result = ' '.join(resultwords)
        fund_benchmark = result
        abs_details = benchmark_abs_details(start_date,end_date,fund_benchmark,scheme_id)
        return abs_details
    else:
        return None


def benchmark_abs_details(start_date,end_date,fund_benchmark,scheme_id):
    ret = Index.objects.filter(name=fund_benchmark)
    seri = IndexSerializer(ret,many=True)
    Index_details = seri.data
    if Index_details:
        Index_details = Index_details[0]
        index = Index_details['id']
        start_nav = IndexData.get_price_for_date(index,start_date)
        end_nav = IndexData.get_price_for_date(index,end_date)
        pct = (end_nav - start_nav) / (start_nav)
        abs_ptc = todo.util.float_round(pct*100, 2, ceil)
        return abs_ptc
    else:
        return None





