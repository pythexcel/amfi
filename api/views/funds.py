from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import generics

from todo.models import AMC, Scheme, Nav

from todo.serializers import AMCSerializer


# @api_view()
# def get_fund_houses():
#     AMC.objects.all()
#     pass

class ListAmc(generics.ListAPIView):
    queryset=AMC.objects.all()
    serializer_class=AMCSerializer