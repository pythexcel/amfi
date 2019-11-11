from todo.models import AMC, Scheme, Nav, Index
from amc.models import Scheme_AUM, Scheme_Portfolio_Data , Scheme_TER
import datetime
from django.db.models import Max

from collections import Counter

def update_scheme_clean_name():
    all = Scheme.objects.all()
    for scheme in all:
        clean_name = scheme.get_clean_name()
        Scheme.objects.filter(pk=scheme.id).update(clean_name=clean_name)
        print("updating clean name for ", getattr(scheme, "fund_name"), " with " , clean_name)

def health_check():


    # general health check for all cron jobs running and reporting
    ter_health_check()
    return {
        # "duplicate_schemes": scheme_health_check(),
        # "aaum_data_check": aum_health_check()

        # also every scheme should have an category, sub category assign. cannot be empty. 
        # add a check for that
        
    }


def scheme_health_check():

    # for scheme in Scheme.objects.raw("select * from todo_scheme where scheme_category = 'Close Ended Schemes' "):
    #     Nav.objects.filter(scheme=getattr(scheme, "id")).delete()

    # find duplicate scheme
    scheme_names = []
    for scheme in Scheme.objects.all():
        scheme_names.append(getattr(scheme, "fund_name"))

    print("duplicate scheme names")
    items = [k for k, v in Counter(scheme_names).items() if v > 1]
    print(items)

    return items
    
    """
    delete FROM `amc_scheme_ter` where scheme_id = 741;
    delete from amc_scheme_portfolio_data where scheme_id = 741;
    delete FROM `amc_scheme_aum` WHERE `scheme_id` = 741;
    delete FROM `stats_schemestats` WHERE `scheme_id` = 741;
    delete FROM `todo_nav` where scheme_id = 741;
    DELETE FROM `todo_scheme` WHERE `todo_scheme`.`id` = 741;

    """

    pass


def portfolio_health_check():

    for amc in AMC.objects.all():
        # id = getattr(amc, "id")

        schemes = Scheme.objects.filter(amc=amc)

        for scheme in schemes:
            ports = Scheme_Portfolio_Data.objects.filter(
                scheme=scheme, date__gt=datetime.datetime(2019, 1, 1)).order_by('date')

            if ports.count() == 0:
                print("portfolio not found for this scheme at all",
                      getattr(scheme, "fund_name"))


def aum_health_check():

    # for now check if we have current year aum data atleast before going back too much

    # Scheme.objects.all()

    for amc in AMC.objects.all():
        # id = getattr(amc, "id")

        schemes = Scheme.objects.filter(amc=amc)

        for scheme in schemes:
            aums = Scheme_AUM.objects.filter(
                scheme=scheme, date__gt=datetime.datetime(2019, 1, 1)).order_by('date')

            if aums.count() == 0:
                print("aaum not found for this scheme at all",
                      getattr(scheme, "fund_name"))
                # print("all good")
            #     pass
            # else:
            #     print("amc name ", getattr(amc, "name"))
            #     print("scheme name ", getattr(scheme, "fund_name"))
            #     for aum in aums:
            #         print(getattr(aum, "date"), " ==== ", getattr(aum, "aum"))

    return {}


def ter_health_check():

    # for now check if we have current year aum data atleast before going back too much

    for amc in AMC.objects.all():
        # id = getattr(amc, "id")

        schemes = Scheme.objects.filter(amc=amc)

        for scheme in schemes:
            aums = Scheme_TER.objects.filter(
                scheme=scheme, date__gt=datetime.datetime(2019, 1, 1)).order_by('date')

            if aums.count() == 0:
                print("ter not found for this scheme at all",
                      getattr(scheme, "fund_name"))
                # print("all good")
            #     pass
            # else:
            #     print("amc name ", getattr(amc, "name"))
            #     print("scheme name ", getattr(scheme, "fund_name"))
            #     for aum in aums:
            #         print(getattr(aum, "date"), " ==== ", getattr(aum, "aum"))

    return {}
