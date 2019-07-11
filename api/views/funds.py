from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import generics

from todo.models import AMC, Scheme, Nav

from todo.serializers import AMCSerializer, SchemeSerializer


@api_view()
def get_schemes(request, amc_id):
    ret = Scheme.objects.all().filter(amc=amc_id)
    print(ret.query)

    ser = SchemeSerializer(ret, many=True)
    return Response(ser.data)


@api_view()
def get_fund_categories(request):
    ret = Scheme.objects.get_category_types()
    ser = SchemeSerializer(ret, many=True)
    return Response(ser.data)

class ListAmc(generics.ListAPIView):
    queryset = AMC.objects.all()
    serializer_class = AMCSerializer
