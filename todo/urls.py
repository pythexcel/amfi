from rest_framework.routers import DefaultRouter
from todo.views import rolling_return, abs_return
from django.urls import path, include, re_path as url

router = DefaultRouter()


import os


# router.register(r'todo', TodoViewSet, basename='todo')


# urlpatterns = [
#     url(r'^rolling_return/(?P<amfi>\d+)/$',
#         rolling_return, name='rolling_return'),
#     url(r'^abs_return/(?P<amfi>\d+)/$', abs_return, name='abs_return'),
# ]

# urlpatterns = urlpatterns + router.urls