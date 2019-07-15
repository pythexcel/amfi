from todo.models import Scheme, AMC, Nav
from stats.models import SchemeStats, SchemeRolling
from django.db.models import Q
import datetime
import json
from django.core.serializers.json import DjangoJSONEncoder

# in this we have calculate year and montly rolling return data
# i.e return for jan, feb, march etc
# and return for year 17-18, 18-19 etc


def rolling_return():
    # rolling return will work once a montly only and will refresh all data in table for all schemes
    rolling_query = Scheme.objects.filter().all()

    print(rolling_query.query)

    for scheme in rolling_query:
        calculate_rolling(scheme)
        break


def calculate_rolling(scheme):

    end_date = datetime.date.today() - datetime.timedelta(days=0)
    start_date = end_date - datetime.timedelta(days=365*5)
    scheme.rolling_return(start_date, end_date)

    pass
