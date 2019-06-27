from todo.jobs import scheduler , download_mf
from rest_framework.routers import DefaultRouter
from todo.views import UserAuth, UserRegister, rolling_return, abs_return
from django.urls import path, include, re_path as url


"""
FULL CRUD OPERATION FOR TODO
"""
router = DefaultRouter()

"""
FULL CRUD OPERATION FOR TODO
"""
# router.register(r'todo', TodoViewSet, basename='todo')


urlpatterns = [
    url(r'^rolling_return/(?P<amfi>\d+)/$',
        rolling_return, name='rolling_return'),
    url(r'^abs_return/(?P<amfi>\d+)/$', abs_return, name='abs_return'),
    url(r'^login/$', UserAuth.as_view()),
    url(r'^register/$', UserRegister.as_view()),
]

urlpatterns = urlpatterns + router.urls



# download_mf()
# scheduler.start()
