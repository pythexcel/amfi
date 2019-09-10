from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import generics

from todo.models import AMC, Scheme, Nav

from django.db.models import Q

from todo.serializers import AMCSerializer, SchemeSerializer


@api_view()
def get_amcs(request):
    ret = AMC.objects.all()
    ser = AMCSerializer(ret, many=True)
    return Response(ser.data)


@api_view()
def get_schemes(request, amc_id):
    ret = Scheme.objects.all().filter(amc=amc_id)
    ser = SchemeSerializer(ret, many=True)
    return Response(ser.data)


@api_view()
def get_fund_categories(request):
    ret = Scheme.objects.get_category_types()
    return Response(ret)


@api_view()
def get_funds(request, type, sub_type):
    ret = Scheme.objects.get_funds(type=type, sub_type=sub_type)
    ser = SchemeSerializer(ret, many=True)
    return Response(ser.data)


@api_view()
def get_fund_subcategories(request, type):
    ret = Scheme.objects.get_sub_category_types(type)
    return Response(ret)


class ListAmc(generics.ListAPIView):
    queryset = AMC.objects.all()
    serializer_class = AMCSerializer
