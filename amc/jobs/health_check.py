from todo.models import AMC, Scheme, Nav, Index
from amc.models import Scheme_AUM
import datetime
from django.db.models import Max


def health_check():
    # general health check for all cron jobs running and reporting

    ret = aum_health_check()

    print("nav health check")
    print(ret)

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
