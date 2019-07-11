from django.urls import path, include, re_path as url
from api.views.returns import rolling_return, abs_return
from api.views.ping import ping
from api.views.funds import ListAmc, get_schemes

from rest_framework.routers import DefaultRouter


router = DefaultRouter()

urlpatterns = [
    url(r'^return/rolling/(?P<amfi>\d+)/$',
        rolling_return, name='rolling_return'),
    url(r'^return/abs/(?P<amfi>\d+)/$', abs_return, name='abs_return'),
    url(r'^ping', ping),
    url(r'^funds/amc', ListAmc.as_view()),
    url(r'^funds/scheme/(?P<amc_id>\d+)/$', get_schemes)
]

urlpatterns = urlpatterns + router.urls
