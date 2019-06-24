from todo.jobs import scheduler
from rest_framework.routers import DefaultRouter
from todo.views import UserAuth, UserRegister, fetch_nav
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
    path('nav', fetch_nav, name='nav'),
    url(r'^login/$', UserAuth.as_view()),
    url(r'^register/$', UserRegister.as_view()),
]

urlpatterns = urlpatterns + router.urls


scheduler.start()
