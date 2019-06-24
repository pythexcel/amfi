from rest_framework.routers import DefaultRouter
from todo.views import UserAuth, UserRegister
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
    url(r'^login/$', UserAuth.as_view()),
    url(r'^register/$', UserRegister.as_view()),
]

urlpatterns = urlpatterns + router.urls

from todo.jobs import scheduler

scheduler.start()
