from django.db import models
from django.db.models import Q

from rest_framework import serializers

import todo.util

import pandas as pd

import datetime
import re
from math import ceil
from dateutil.relativedelta import relativedelta


class MFDownload(models.Model):
    amc_id = models.IntegerField(null=False)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    start_time = models.DateTimeField(null=False)
    end_time = models.DateTimeField(null=True)
    retry = models.IntegerField(null=False, default=0)
    has_data = models.BooleanField(null=False, default=True)

# https://medium.com/@MicroPyramid/django-model-managers-and-properties-564ef668a04c


class AMCManager(models.Manager):
    def match_amc_with_short_name(self, short_name):
        if "Parag Parikh" in short_name:
            short_name = "PPFAS"

        if "Mahindra" in short_name:
            short_name = "Mahindra Mutual Fund"
            amcs = self.filter(name=short_name)
            if amcs.count() > 0:
                return amcs.first()

        amcs = self.filter(name__icontains=short_name)
        if amcs.count() > 0:
            return amcs.first()
        else:
            return False
    pass


class AMC(models.Model):
    name = models.CharField(max_length=255, unique=True)
    amc_no = models.IntegerField(null=False, unique=True)
    parsed = models.BooleanField(null=False, default=False)
    next_amc_no = models.IntegerField(null=False, default=0)
    logo = models.CharField(max_length=255, null=True)

    objects = AMCManager()


class SchemeManager(models.Manager):
    # for now working with open ended schems only
    def get_queryset(self):
        return super().get_queryset().filter(scheme_category='Open Ended Schemes', fund_active=True)

    """
    getting expect category types are
    [
        "Equity Scheme",
        "Debt Scheme",
        "Hybrid Scheme",   //balance etc type
        "Other Scheme", // index funds, fof funds (fund of fund)
        "Income", //these are generally fix internal funds fix income funds
        "Growth", // very few funds classified as growth
        "Gilt",
        "Floating Rate", //there are very fund floating rate funds like 2=3
        "Solution Oriented Scheme" //like retainment, child education etc
    ]
    """

    def get_category_types(self):
        return self.values_list("scheme_type", flat=True).distinct()

    # this function is to return sub types of a scheme. e.g to get sub types of debt scheme
    def get_sub_category_types(self, type):
        return self.filter(scheme_type__icontains=type).values_list("scheme_sub_type", flat=True).distinct()

    def get_funds(self, type=None, sub_type=None, amc=None):
        if type is None and amc is None:
            raise Exception("either type or amc is needed")

        filter = None

        if type is not None:
            filter = Q(scheme_type=type)

        if amc is not None:
            if type is not None:
                filter = Q(scheme_type=type) & Q(amc=amc)
                print(filter)
            else:
                filter = Q(amc=amc)

        if sub_type is not None:
            filter &= Q(scheme_sub_type=sub_type)

        print(self.filter(filter))

        return self.filter(filter)

    def get_actual_scheme_names_for_amc(self, amc):
        pass


# scheme_types_equity = [
#     "Contra Fund",   # NIFTY 100 TRI
#     "Dividend Yield Fund",  # NIFTY 100 TRI
#     "Large Cap Fund",  # NIFTY 100 TRI
#     "ELSS",
#     "Focussed Fund",
#     "Large & Mid Cap Fund",
#     "Multi-Cap Fund",
#     "Mid Cap Fund",
#     "Sectoral/ Thematic",
#     "Value Fund",
#     "Mid Cap Fund",
#     "Small Cap Fund",
#     "Arbitrage Fund",
#     "Aggressive Hybrid Fund",
#     "Conservative Hybrid Fund",
#     "Dynamic Asset Allocation Fund",
#     "Index Fund",
#     "Fund of Funds",  # like us funds etc
#     "Retirement Funds",  # solution oriented funds
#     "Children Fund"  # solution oriented funds
# ]

# scheme_types_debt = [
#     "Banking and PSU Fund",
#     "Corporate Bond Fund",
#     "Credit Risk Fund",
#     "Dynamic Bond Fund",
#     "Floater Fund",
#     "Fund of Funds - Debt",
#     "Gilt Fund",
#     "Liquid Fund",
#     "Medium Duration Fund",
#     "Medium to Long Duration Fund",
#     "Money Market Fund",
#     "Overnight Fund",
#     "Short Duration Fund",
#     "Ultra Short Duration Fund"
# ]

debt_fund = [
    {"Text": "Overnight Fund", "Value": "25"},
    {"Text": "Liquid Fund", "Value": "26"},
    {"Text": "Ultra Short Duration Fund", "Value": "27"},
    {"Text": "Low Duration Fund", "Value": "28"},
    {"Text": "Money Market Fund", "Value": "29"},
    {"Text": "Short Duration Fund", "Value": "30"},
    {"Text": "Medium Duration Fund", "Value": "31"},
    {"Text": "Medium to Long Duration Fund", "Value": "32"},
    {"Text": "Long Duration Fund", "Value": "33"},
    {"Text": "Dynamic Bond", "Value": "34"},
    {"Text": "Corporate Bond Fund", "Value": "35"},
    {"Text": "Credit Risk Fund", "Value": "36"},
    {"Text": "Banking and PSU Fund", "Value": "37"},
    {"Text": "Gilt Fund", "Value": "38"},
    {"Text": "Gilt Fund with 10 year constant duration", "Value": "39"},
    {"Text": "Floater Fund", "Value": "40"}
]


solution_fund = [
    {"Text": "Retirement Fund", "Value": "48"},
    {"Text": "Children’s Fund", "Value": "49"}
]

equity_fund = [
    {"Text": "Multi Cap Fund", "Value": "14"},
    {"Text": "Large Cap Fund", "Value": "15"},
    {"Text": "Large & Mid Cap Fund", "Value": "16"},
    {"Text": "Mid Cap Fund", "Value": "17"},
    {"Text": "Small Cap Fund", "Value": "18"},
    {"Text": "Dividend Yield Fund", "Value": "19"},
    {"Text": "Value Fund", "Value": "20"},
    {"Text": "Contra Fund", "Value": "21"},
    {"Text": "Focussed Fund", "Value": "22"},
    {"Text": "Sectoral/ Thematic", "Value": "23"},
    {"Text": "ELSS", "Value": "24"}]

hybrid_fund = [
    {"Text": "Conservative Hybrid Fund", "Value": "41"},
    {"Text": "Balanced Hybrid Fund", "Value": "42"},
    {"Text": "Aggressive Hybrid Fund", "Value": "43"},
    {"Text": "Dynamic Asset Allocation or Balanced Advantage", "Value": "44"},
    {"Text": "Multi Asset Allocation", "Value": "45"},
    {"Text": "Arbitrage Fund", "Value": "46"},
    {"Text": "Equity Savings", "Value": "47"}
]

other_fund = [
    {"Text": "Index Funds", "Value": "50"},
    {"Text": "Gold ETF", "Value": "51"},
    {"Text": "Other  ETFs", "Value": "52"},
    {"Text": "FoF Overseas", "Value": "53"},
    {"Text": "FoF Domestic", "Value": "54"}
]

fund_categorization = {
    "Debt Scheme": debt_fund,
    "Equity Scheme": equity_fund,
    "Hybrid Scheme": hybrid_fund,
    "Other Scheme": other_fund,
    "Solution Oriented Scheme": solution_fund
}


class Scheme_Info(models.Model):
    scheme = models.ForeignKey(
        "Scheme",
        on_delete=models.CASCADE
    )
    benchmark = models.CharField(max_length=255, null=False)
    inception = models.DateField(null=False)


class Scheme(models.Model):
    amc = models.ForeignKey(
        'AMC',
        on_delete=models.CASCADE,
    )
    # this is mainly for open ended or close ended
    scheme_category = models.CharField(max_length=255, null=False)
    # this is for equity debt etc
    scheme_type = models.CharField(max_length=255, null=False)
    # this is for type i.e mid cap, large cap etc
    scheme_sub_type = models.CharField(max_length=255, null=False)
    fund_code = models.CharField(
        max_length=255, null=False, unique=True)  # amfi code
    fund_name = models.CharField(max_length=255, null=False)  # name
    fund_option = models.CharField(
        max_length=255, null=False)  # grown or what kind
    fund_type = models.CharField(
        max_length=255, null=False)  # direct or regular
    fund_active = models.BooleanField(default=True)
    # saving the orignal line from csv. required for debugging
    line = models.CharField(max_length=255)
    clean_name = models.CharField(max_length=255)

    objects = SchemeManager()

    # def get_category_types(self):
    # return ["Equity", "Debt", "Hybrid", "Others", "Solution"]

    @staticmethod
    def find_fund_with_name(match_string):
        match_string = todo.util.clean_fund_string(match_string)
        return Scheme.objects.filter(clean_name=match_string).first()


    def get_clean_name(self):
        name = getattr(self, "fund_name")
        return todo.util.clean_fund_string(name)
    # clean_name = property(get_clean_name)

    def is_closed_ended(self):
        s_cat = getattr(self, "scheme_category")
        if s_cat.contains("Closed"):
            return True

        return False

    def is_open_ended(self):
        s_cat = getattr(self, "scheme_category")
        if "Open" in s_cat:
            return True

        return False

    def is_debt(self):
        s_type = getattr(self, "scheme_type")
        if "Debt" in s_type:
            return True

        return False

    def is_equity(self):
        s_type = getattr(self, "scheme_type")
        if "Equity" in s_type:
            return True

        return False

    def is_index(self):
        s_type = getattr(self, "scheme_type")
        s_sub_type = getattr(self, "scheme_sub_type")

        if "Index" in s_sub_type:
            return True

        return False

    # this is for calcuation's with base reference of any year but 1st and last of year
    def previous_yr_abs(self, years=1, start_year=0):
        # years how many years to go back
        # start_year which year to start from
        # abs weather absolute return or annulized return

        end_date = datetime.date(datetime.date.today(
        ).year - start_year, 1, 1) - datetime.timedelta(days=1)
        # 1 DAY BECAUSE we need to find the date 31 dec instead of 1jan of the previous

        start_date = end_date - datetime.timedelta(days=365*years)

        ret = self.abs_return(start_date, end_date)
        if years > 1:
            cagr = todo.util.cagr(
                ret["start_nav"], ret["end_nav"], years) * 100
            ret["cagr"] = todo.util.float_round(cagr, 2, ceil)

        return ret

    # this has all caculate with base reference as today
    def previous_yr_abs_today(self, years=1, offset_days=0):
        # how many years to go back
        # offset in days, if start from today or few days back
        # abs weather absolute return or annulized return
        end_date = datetime.date.today() - datetime.timedelta(days=offset_days)
        start_date = end_date - datetime.timedelta(days=365*years)

        ret = self.abs_return(start_date, end_date)

        if years > 1:
            cagr = todo.util.cagr(
                ret["start_nav"], ret["end_nav"], years) * 100
            ret["cagr"] = todo.util.float_round(cagr, 2, ceil)

        return ret

    def ytd_abs(self, offset_days=0):
        end_date = datetime.date.today() - datetime.timedelta(days=offset_days)
        start_date = datetime.date(datetime.date.today().year, 1, 1)

        return self.abs_return(start_date, end_date)

    def since_start(self, offset_days=0):
        end_date = datetime.date.today()
        nav, begin_date = Nav.get_nav_begining(self)

        print("nav ", nav, " begin date ", begin_date)

        difference_in_years = relativedelta(end_date, begin_date).years

        ret = self.abs_return(begin_date, end_date)

        if difference_in_years > 1:
            cagr = todo.util.cagr(
                ret["start_nav"], ret["end_nav"], difference_in_years) * 100
            ret["cagr"] = todo.util.float_round(cagr, 2, ceil)
            ret["year_since_begin"] = difference_in_years

        return ret

    def abs_return(self, start_date, end_date):
        start_nav = Nav.get_nav_for_date(self, start_date)
        end_nav = Nav.get_nav_for_date(self, end_date)

        pct = (end_nav - start_nav) / (start_nav)

        return {
            "start_nav": start_nav,
            "start_date": start_date,
            "end_nav": end_nav,
            "end_date": end_date,
            "pct": todo.util.float_round(pct*100, 2, ceil)
        }

    def rolling_yr_today(self, freq="M", years=1, offset_days=0):
        # how many years to go back
        # offset in days, if start from today or few days back
        # abs weather absolute return or annulized return
        end_date = datetime.date.today() - datetime.timedelta(days=offset_days)
        start_date = end_date - datetime.timedelta(days=365*years)

        return self.rolling_return(start_date, end_date, freq)

    # //https://stackoverflow.com/questions/35339139/where-is-the-documentation-on-pandas-freq-tags
    # calculate rolling return for any scheme and frequency
    def rolling_return(self, start_date, end_date, freq="M"):
        f = Q(scheme=self)
        f &= Q(date__gt=start_date)
        f &= Q(date__lt=end_date)

        navs = Nav.objects.filter(f).order_by("date")
        print(navs.query)
        ser = NavSerializer(navs, many=True)

        df = pd.DataFrame(ser.data, columns=["nav", "date"])

        start_date = df.iloc[0]["date"]
        end_date = df.iloc[len(df.index) - 1]["date"]

        idx = pd.date_range(start_date, end_date)

        df['Datetime'] = pd.to_datetime(df["date"])

        df = df.set_index("Datetime")
        df = df.reindex(idx, method='ffill')

        df = df.drop(['date'], axis=1)

        df1 = df.asfreq(freq)

        def pct_change(row):
            # print(row)
            return 100 * (1 - df.iloc[0].nav / row.nav)

        df1['pct'] = df1.apply(pct_change, axis=1)

        # df.pct_change() this is not useful. we need calculate change from first value

        print(df1)

        return df1

    class Meta:
        unique_together = ("amc", "fund_code")

    @staticmethod
    def get_fund_categorization():
        return fund_categorization


class Nav(models.Model):
    scheme = models.ForeignKey(
        'Scheme',
        on_delete=models.CASCADE,
    )
    nav = models.FloatField(null=False)
    date = models.DateField(null=False)

    class Meta:
        unique_together = ("scheme", "date")

    @staticmethod
    def count_navs_date(date):
        return Nav.objects.filter(date=date).count()

    @staticmethod
    def get_latest_nav_date():
        nav = Nav.objects.all().order_by("-date").first()
        return getattr(nav, "date")

    @staticmethod
    def get_nav_begining(scheme):
        # this will return the nav value and date since the scheme begain i.e the first data which we have
        nav = Nav.objects.filter(scheme=scheme).order_by("date").first()
        return getattr(nav, "nav"), getattr(nav, "date")

    @staticmethod
    def get_nav_for_date(scheme, date, extrapolateNav=True):
        # this can be optmized by cache because we are calculating the date frame again and again
        # for large calculation it can be improved
        # this function will get nav for date and will interpolate if nav doesn't exist
        try:
            navs = Nav.objects.get(scheme=scheme, date=date)
            start_nav = navs.nav
            # data exists problem solved
        except Nav.DoesNotExist:

            if extrapolateNav == False:
                raise Exception(
                    "Nav doesn't exist and extrapolate is false  for date", date)
            # data doesn't exist. we need to find nearest set of data's and interpolate based on it
            print("nav doesn't existing will intrapolate")

            date_delta_end = date - datetime.timedelta(days=7)
            date_delta_start = date + datetime.timedelta(days=7)
            f = Q(date__gt=date_delta_end) & Q(
                date__lt=date_delta_start) & Q(scheme=scheme)

            navs = Nav.objects.filter(f)
            if navs.count() > 0:
                ser = NavSerializer(navs, many=True)
                df = todo.util.get_date_index_data(ser.data)
                print(df)

                start_date = date_delta_end
                end_date = date_delta_start

                df = todo.util.fill_date_frame_data(df, start_date, end_date)
                # print(df)
                start_nav = df.loc[date.strftime("%Y-%m-%d")]["nav"]
            else:
                raise ValueError(
                    "unable to get nav value at all, check your date", date)

        return start_nav


class NavSerializer(serializers.ModelSerializer):
    class Meta:
        model = Nav
        fields = '__all__'


class Index(models.Model):
    name = models.CharField(max_length=255)
    type = models.CharField(max_length=255)
    start_date = models.DateField(null=False)
    end_date = models.DateField(null=False)
    parsed = models.BooleanField(default=False)

    @staticmethod
    def get_latest_index_date():
        return Index.objects.raw("SELECT MAX(date) as max_date, index_id, todo_index.id, todo_index.name as name, todo_index.type as type FROM `todo_indexdata` JOIN todo_index on todo_index.id = index_id GROUP by index_id")

    # this is for calcuation's with base reference of any year but 1st and last of year

    def previous_yr_abs(self, years=1, start_year=0):
        # years how many years to go back
        # start_year which year to start from
        # abs weather absolute return or annulized return

        end_date = datetime.date(datetime.date.today(
        ).year - start_year, 1, 1) - datetime.timedelta(days=1)
        # 1 DAY BECAUSE we need to find the date 31 dec instead of 1jan of the previous

        start_date = end_date - datetime.timedelta(days=365*years)

        ret = self.abs_return(start_date, end_date)
        if years > 1:
            cagr = todo.util.cagr(
                ret["start_price"], ret["end_price"], years) * 100
            ret["cagr"] = todo.util.float_round(cagr, 2, ceil)

        return ret

    # this has all caculate with base reference as today
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

    def ytd_abs(self, offset_days=0):
        end_date = datetime.date.today() - datetime.timedelta(days=offset_days)
        start_date = datetime.date(datetime.date.today().year, 1, 1)

        return self.abs_return(start_date, end_date)

    def since_start(self, offset_days=0):
        end_date = datetime.date.today()
        nav, begin_date = IndexData.get_price_begining(self)

        print("price ", nav, " begin date ", begin_date)

        difference_in_years = relativedelta(end_date, begin_date).years

        ret = self.abs_return(begin_date, end_date)

        if difference_in_years > 1:
            cagr = todo.util.cagr(
                ret["start_price"], ret["end_price"], difference_in_years) * 100
            ret["cagr"] = todo.util.float_round(cagr, 2, ceil)
            ret["year_since_begin"] = difference_in_years

        return ret

    def abs_return(self, start_date, end_date):
        start_nav = IndexData.get_price_for_date(self, start_date)
        end_nav = IndexData.get_price_for_date(self, end_date)

        pct = (end_nav - start_nav) / (start_nav)

        return {
            "start_price": start_nav,
            "start_date": start_date,
            "end_price": end_nav,
            "end_date": end_date,
            "pct": todo.util.float_round(pct*100, 2, ceil)
        }

    class Meta:
        unique_together = ("name", "type")


class IndexData(models.Model):
    index = models.ForeignKey(
        'Index',
        on_delete=models.CASCADE
    )
    date = models.DateField(null=False)
    open = models.FloatField(null=False)
    close = models.FloatField(null=False)
    high = models.FloatField(null=False)
    low = models.FloatField(null=False)
    pe = models.FloatField(null=True)
    pb = models.FloatField(null=True)
    div = models.FloatField(null=True)

    @staticmethod
    def get_price_begining(index):
        # this will return the price from the first value which we have
        index_data = IndexData.objects.filter(
            index=index).order_by("date").first()
        return getattr(index_data, "close"), getattr(index_data, "date")

    @staticmethod
    def get_price_for_date(index, date):
        # this can be optmized by cache because we are calculating the date frame again and again
        # for large calculation it can be improved
        # this function will get nav for date and will interpolate if nav doesn't exist
        try:
            index_data = IndexData.objects.get(index=index, date=date)
            start_nav = getattr(index_data, "close")
            # data exists problem solved
        except IndexData.DoesNotExist:

            # data doesn't exist. we need to find nearest set of data's and interpolate based on it
            print("price doesn't existing will intrapolate")

            date_delta_end = date - datetime.timedelta(days=7)
            date_delta_start = date + datetime.timedelta(days=7)
            f = Q(date__gt=date_delta_end) & Q(
                date__lt=date_delta_start) & Q(index=index)

            datas = IndexData.objects.filter(f)
            if datas.count() > 0:
                ser = IndexDataSerializer(datas, many=True)
                df = todo.util.get_priceindex_data(ser.data)
                print(df)

                start_date = date_delta_end
                end_date = date_delta_start

                df = todo.util.fill_date_frame_data(df, start_date, end_date)
                # print(df)
                start_nav = df.loc[date.strftime("%Y-%m-%d")]["close"]
            else:
                raise ValueError(
                    "unable to get nav value at all, check your date", date)

        return start_nav


class IndexDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = IndexData
        fields = '__all__'
