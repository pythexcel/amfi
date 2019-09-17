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
def get_funds_amc(request,type,sub_type):
    """
    
    Returns the AMC based on schemes type and sub_type.
    
    """
    ret = Scheme.objects.get_funds(type=type,sub_type=sub_type)
    ser = SchemeSerializer(ret, many=True)
    unique = []
    for data in ser.data:
        if data['amc'] not in unique:
            unique.append(data['amc'])
        else:
            pass
    response = []    
    for elem in unique:
        resp = AMC.objects.get(id=elem)
        serial = AMCSerializer(resp,many=False)
        response.append(serial.data)
    return Response(response)

@api_view()
def get_funds_schemes(request,amc,type,sub_type):
    """
    
    Returns the Schemes based on schemes type and sub_type and amc.
    
    """
    ret = Scheme.objects.get_funds(amc=amc,type=type,sub_type=sub_type)
    ser = SchemeSerializer(ret, many=True)
    return Response(ser.data)


@api_view()
def get_funds_schemes_type(request,amc,type):
    """
    
    Returns the schemes based on schemes amc and type.
    
    """
    ret = Scheme.objects.get_funds(amc=amc,type=type)
    ser = SchemeSerializer(ret, many=True)
    return Response(ser.data)


@api_view()
def get_fund_subcategories(request, type):
    ret = Scheme.objects.get_sub_category_types(type)
    return Response(ret)


class ListAmc(generics.ListAPIView):
    queryset = AMC.objects.all()
    serializer_class = AMCSerializer
