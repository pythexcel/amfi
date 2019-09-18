from django.urls import path, include, re_path as url
from api.views.returns import rolling_return, abs_return
from api.views.ping import ping
#from api.views.funds import ListAmc, get_schemes, get_fund_categories, get_fund_subcategories, get_funds,get_funds_amc,get_funds_schemes,get_funds_schemes_type
from api.views.dashboard import (nav_check, nav_run_script, get_process_logs, index_check, index_run_script, nav_last_update, schem_list,
                                 schem_update_list, nav_ten, get_amcs)

from api.views.funds import get_funds_amc, get_funds_schemes, get_funds_schemes_type, fix_name_mismatch, get_probable_list_for_mismatch, ListAmc, NameMismatchList, get_amcs, get_schemes, get_fund_categories, get_fund_subcategories, get_funds

from rest_framework.routers import DefaultRouter


router = DefaultRouter()

urlpatterns = [
    url(r'^return/rolling/(?P<amfi>\d+)/$',
        rolling_return, name='rolling_return'),
    url(r'^return/abs/(?P<amfi>\d+)/$', abs_return, name='abs_return'),
    url(r'^ping', ping),
    url(r'^amc', get_amcs),
    url(r'^funds/amc', ListAmc.as_view()),
    url(r'^funds/scheme/(?P<amc_id>\d+)/$', get_schemes),
    url(r'^funds/category', get_fund_categories),
    url(r'^funds/subcategory/(?P<type>[\w|\W]+)/$', get_fund_subcategories),

    url(r'^get_funds/(?P<type>[\w|\W]+)/(?P<sub_type>[\w|\W]+)/$', get_funds),
    url(r'^get_funds_scheme/amc/(?P<type>[\w|\W]+)/(?P<sub_type>[\w|\W]+)/$', get_funds_amc),
    url(
        r'^get_funds_schemes_type/(?P<amc>\d+)/(?P<type>[\w|\W]+)/(?P<sub_type>[\w|\W]+)/$', get_funds_schemes),
    url(r'^get_funds_schemes/(?P<amc>\d+)/(?P<type>[\w|\W]+)/$', get_funds_schemes_type),



    # scheme name mismatch related api's

    url(r'^get_name_mismatch', NameMismatchList.as_view()),
    url(r'^get_probable_list_for_mismatch/(?P<amc>[\w|\W]+)/$',
        get_probable_list_for_mismatch),
    url(r'^fix_name_mismatch/(?P<mismatch_id>\d+)/(?P<scheme_id>\d+)/$', fix_name_mismatch)


    # need to add code for full new amc itself.
    # it seem in the last week DHFL got closed and and new amc PGIM
]


# need to admin authentication to this will do it later on
urlpatterns2 = [
    url(r'^dashboard/get_process_logs/(?P<type>[\w|\W]+)/$', get_process_logs),

    url(r'^dashboard/summary/dailynav/runscript', nav_run_script),
    url(r'^dashboard/summary/dailynav', nav_check),


    url(r'^dashboard/summary/dailyindex', index_check),
    url(r'^dashboard/summary/dailyindex/runscript', index_run_script),


    url(r'^dashboard/amc', get_amcs),
    url(r'^dashboard/unupdated_nav', nav_ten),
    url(r'^dashboard/updated_scheme', schem_update_list),
    url(r'^dashboard/nav_last', nav_last_update),
    url(r'^dashboard/scheme', schem_list)


]


# index page for admin dashboard route needed
# this will be a dedicated page for only all indexes we are tracking
# mainly need to show index name, last nav, pe/pb ration's etc depend on what we have in db

indexPageRoutes = [
    # url(r'^dashboard/indexs/get_list/$', lambda: pass),
    # url(r'^dashboard/indexs/runCron/$', lambda: pass),
    # need to also figure out a way to see output for a running script
    # maybe we should just run via command and community the output. thats the simplest
]


urlpatterns = urlpatterns + urlpatterns2 + router.urls
