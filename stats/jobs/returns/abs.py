from todo.models import Scheme, AMC, Nav,Index
from stats.models import SchemeStats
from django.db.models import Q
import datetime
from rest_framework import serializers
import json
from dateutil.relativedelta import relativedelta
import datetime
from datetime import datetime,timedelta
from django.core.serializers.json import DjangoJSONEncoder
from todo.models import Index_scheme_mapping

# this will caculate 1yr return of all funds
# problem is nav is daily calculated and 1yr return will change daily
# need to find an effecient way to do this fast accross all schemes


def abs_return():
    # the logic to this is we will calculate abs return for all scheme daily annd store it db
    # even if nav is not present for that day it will extrapolate and calculate based on nearest nav
    # and update to db the scheme 1yr return etc
    # this is the most easist logic for now that always calculate and update to db
    # more effecient way need to be thought of but first need to start with something simple

    query = SchemeStats.objects.filter(~Q(calc_date=datetime.datetime.today()))

    schemes = []
    if query.count() > 0:
        # scheme_stat = query.first()
        for scheme_stat in query:
            schemes.append(Scheme.objects.get(
                pk=getattr(scheme_stat, "scheme")))
    else:
         # see if any new schemes are added
        schemestat_ids = SchemeStats.objects.values_list(
            'scheme', flat=True).distinct()
        # print(schemestat_ids)
        missing_stats = Scheme.objects.exclude(Q(id__in=schemestat_ids))

        # print(missing_stats.query)

        if missing_stats.count() > 0:
            schemes = missing_stats

    for scheme in schemes:
        calc_stats_for_scheme(scheme)
    pass

# this is data of yearly return e.g return between 2017-2018 etc
# this doesn't change with time as such unless full year changes


def calc_stats_for_scheme(scheme):
    json_dump = ""
    try:
        ret = scheme.previous_yr_abs_today()
        one_year_abs_ret = ret["pct"]
        # print("one year ret")
        print(ret)
        json_dump += json.dumps(ret, cls=DjangoJSONEncoder)
    except Exception as e:
        print(e)
        one_year_abs_ret = -1
        pass

    try:
        ret = scheme.previous_yr_abs_today(3)
        three_year_abs_ret = ret["pct"]
        three_year_cagr_ret = ret["cagr"]
        print(ret)
        json_dump += json.dumps(ret, cls=DjangoJSONEncoder)
    except:
        three_year_abs_ret = -1
        three_year_cagr_ret = -1
        pass

    try:
        ret = scheme.previous_yr_abs_today(5)
        five_year_abs_ret = ret["pct"]
        five_year_cagr_ret = ret["cagr"]
        print(ret)
        json_dump += json.dumps(ret, cls=DjangoJSONEncoder)
    except:
        five_year_abs_ret = -1
        five_year_cagr_ret = -1
        pass

    try:
        ret = scheme.previous_yr_abs_today(10)
        ten_year_abs_ret = ret["pct"]
        ten_year_cagr_ret = ret["cagr"]
        print(ret)
        json_dump += json.dumps(ret, cls=DjangoJSONEncoder)
    except:
        ten_year_abs_ret = -1
        ten_year_cagr_ret = -1
        pass

    try:
        ret = scheme.since_start()
        since_begin_abs_ret = ret["pct"]
        since_begin_cagr_ret = ret["cagr"]
        print(ret)
        json_dump += json.dumps(ret, cls=DjangoJSONEncoder)
    except:
        since_begin_abs_ret = -1
        since_begin_cagr_ret = -1
        pass

    try:
        stats = SchemeStats.objects.get(schema=scheme)
        stats.delete()
    except:
        pass

    stats = SchemeStats(
        scheme=scheme,
        dump=json_dump,
        calc_date=datetime.datetime.today(),
        one_year_abs_ret=one_year_abs_ret,
        three_year_abs_ret=three_year_abs_ret,
        three_year_cagr_ret=three_year_cagr_ret,
        five_year_abs_ret=five_year_abs_ret,
        five_year_cagr_ret=five_year_cagr_ret,
        ten_year_abs_ret=ten_year_abs_ret,
        ten_year_cagr_ret=ten_year_cagr_ret,
        since_begin_abs_ret=since_begin_abs_ret,
        since_begin_cagr_ret=since_begin_cagr_ret
    )
    stats.save()
    pass




def index_abs_return(index):
    '''
    ret = SchemeStats.objects.values_list(
            'scheme', flat=True).distinct()    
#    for rett in ret:
    scheme_id = 12
    #back = datetime.datetime.today() + relativedelta(months=-12)
    #one_year_back = back.strftime('%Y-%m-%d')
    one_year_ba = "2019-04-04"
    one_year_back = datetime.strptime(one_year_ba, '%Y-%m-%d').date()
    #today = datetime.datetime.today()
    today = "2019-04-02"
    #today_date = today.strftime('%Y-%m-%d')
    start_date = datetime.strptime(today, '%Y-%m-%d').date()
    abss =  Index_scheme_mapping(one_year_back,start_date,scheme_id)
#    print(abss)         

#    three_yrs_ago = datetime.now() - relativedelta(years=3)
    '''
def previous_yr_abs_today(self, years=1, offset_days=0):
    # how many years to go back
    # offset in days, if start from today or few days back
    # abs weather absolute return or annulized return
    end_date = datetime.date.today() - datetime.timedelta(days=offset_days)
    start_date = end_date - datetime.timedelta(days=365*years)

    ret = self.abs_return(start_date, end_date)

    if years > 1:
        cagr = todo.util.cagr(
            ret["start_price"], ret["end_price"], years) * 100
        ret["cagr"] = todo.util.float_round(cagr, 2, ceil)
    return ret

