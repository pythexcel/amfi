from django.test import TestCase
from todo.models import Scheme_Info,SchemeinfoSerializer,Index,IndexSerializer,IndexData
import todo.util
from math import ceil
import numpy as np

maping_dict =[ {"benchmark_name":"S&P BSE 150 MidCap","benchmark":"SPB15MIP"},
                {"benchmark_name":"S&P BSE SENSEX","benchmark":"SENSEX"},
                {"benchmark_name":"S&P BSE AllCap","benchmark":"SPBSAIP"},
                {"benchmark_name":"S&P BSE Enhanced Value","benchmark":"SPBSEVIP"},
                {"benchmark_name":"S&P BSE Teck","benchmark":"SIBTEC"},
                {"benchmark_name":"S&P BSE 500","benchmark":"BSE500"},
                {"benchmark_name":"S&P BSE 200","benchmark":"BSE200"},
                {"benchmark_name":"S&P BSE 100","benchmark":"BSE100"},
                {"benchmark_name":"S&P BSE Small Cap","benchmark":"BSESML"},
                {"benchmark_name":"S&P BSE HC","benchmark":"SI0800"},
                {"benchmark_name":"S&P BSE Sensex","benchmark":"SENSEX"},
                {"benchmark_name":"S&P 500 International","benchmark":"BSE500"},
                {"benchmark_name":"S&P BSE Information Technology","benchmark":"SI1000"},
                {"benchmark_name":"S&P 500","benchmark":"BSE500"},
                {"benchmark_name":"S&P BSE IT","benchmark":"SI1000"},
                {"benchmark_name":"S&P BSE BANKEX","benchmark":"SIBANK"},
                {"benchmark_name":"S&P BSE 500 Shariah","benchmark":"SPBSE5S"},
                {"benchmark_name":"S&P BSE India Infrastructure","benchmark":"INFRA"},
                {"benchmark_name":"S&P BSE Teck","benchmark":"SIBTEC"},
                {"benchmark_name":"S&P BSE Mid Cap","benchmark":"BSEMID"},
                {"benchmark_name":"S&P BSE 250 Large MidCap","benchmark":"SPB25XIP"},
                {"benchmark_name":"S&P BSE Healthcare","benchmark":"SI0800"},
                {"benchmark_name":"S&P BSE 50","benchmark":"SPBSS5IP"},
                {"benchmark_name":"S&P BSE Midcap","benchmark":"BSEMID"},
                {"benchmark_name":"S&P BSE Health Care","benchmark":"SI0800"},
                {"benchmark_name":"S&P BSE 250 Small Cap","benchmark":"SPB25SIP"},
                {"benchmark_name":"S&P BSE PSU","benchmark":"SIBPSU"},
                {"benchmark_name":"S&P BSE HEALTH CARE","benchmark":"SI0800"},
                {"benchmark_name":"S&P BSE PSU","benchmark":"SIBPSU"},

                {"benchmark_name":"NIFTY 50","benchmark":"NIFTY 50"},
                {"benchmark_name":"NIFTY NEXT 50","benchmark":"NIFTY NEXT 50"},
                {"benchmark_name":"NIFTY SMLCAP 100","benchmark":"NIFTY SMLCAP 100"},
                {"benchmark_name":"NIFTY MIDCAP 100","benchmark":"NIFTY MIDCAP 100"},
                {"benchmark_name":"NIFTY 100","benchmark":"NIFTY 100"},
                {"benchmark_name":"NIFTY 500","benchmark":"NIFTY 500"},
                {"benchmark_name":"NIFTY 200","benchmark":"NIFTY 200"},
                {"benchmark_name":"NIFTY MIDCAP 150","benchmark":"NIFTY MIDCAP 150"},
                {"benchmark_name":"NIFTY FMCG","benchmark":"NIFTY FMCG"},
                {"benchmark_name":"NIFTY MNC","benchmark":"NIFTY MNC"},
                {"benchmark_name":"NIFTY INFRA","benchmark":"NIFTY INFRA"},
                {"benchmark_name":"NIFTY MIDCAP 50","benchmark":"NIFTY MIDCAP 50"},
                {"benchmark_name":"NIFTY FULL MIDCAP 100","benchmark":"NIFTY FULL MIDCAP 100"},
                {"benchmark_name":"NIFTY SMLCAP 250","benchmark":"NIFTY SMLCAP 250"},
                {"benchmark_name":"NIFTY SMLCAP 50","benchmark":"NIFTY SMLCAP 50"},
                {"benchmark_name":"NIFTY LARGEMIDCAP 250","benchmark":"NIFTY LARGEMIDCAP 250"}
                
]


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
                fund_benchmark = benchmark
                print(fund_benchmark)
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
        pct = (end_nav - start_nav) / (start_nav)
        if np.isnan(pct) == False:
            abs_ptc = todo.util.float_round(pct*100, 2, ceil)
            return abs_ptc
    else:
        return None