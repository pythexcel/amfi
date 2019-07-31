from todo.models import AMC, Scheme, Nav, Index
from amc.models import Scheme_AUM
import datetime
from django.db.models import Max

from collections import Counter


def health_check():
    # general health check for all cron jobs running and reporting

    scheme_health_check()

    # ret = aum_health_check()

    # print("nav health check")
    # print(ret)

    pass


def scheme_health_check():

    for scheme in Scheme.objects.raw("select * from todo_scheme where scheme_category = 'Close Ended Schemes' "):
        Nav.objects.filter(scheme=getattr(scheme, "id")).delete()

    # find duplicate scheme
    scheme_names = []
    for scheme in Scheme.objects.all():
        scheme_names.append(getattr(scheme, "fund_name"))

    print("duplicate scheme names")
    items = [k for k, v in Counter(scheme_names).items() if v > 1]
    print(items)

    """
    delete FROM `amc_scheme_ter` where scheme_id = 896;
    delete from amc_scheme_portfolio_data where scheme_id = 896;
    delete FROM `amc_scheme_aum` WHERE `scheme_id` = 896;
    delete FROM `stats_schemestats` WHERE `scheme_id` = 896;
    delete FROM `todo_nav` where scheme_id = 896;
    DELETE FROM `todo_scheme` WHERE `todo_scheme`.`id` = 896;

    """

    pass


def aum_health_check():

    # for now check if we have current year aum data atleast before going back too much

    # Scheme.objects.all()

    for amc in AMC.objects.all():
        # id = getattr(amc, "id")

        scheme = Scheme.objects.filter(amc=amc).first()

        aums = Scheme_AUM.objects.filter(
            scheme=scheme, date__gt=datetime.datetime(2019, 1, 1)).order_by('date')

        if aums.count() == 6:
            # print("all good")
            pass
        else:
            print("amc name ", getattr(amc, "name"))
            print("scheme name ", getattr(scheme, "fund_name"))
            for aum in aums:
                print(getattr(aum, "date"), " ==== ", getattr(aum, "aum"))

    return {}
