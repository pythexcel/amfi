from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import generics

from todo.models import AMC, Scheme, Nav

from amc.models import Scheme_Name_Mismatch

from rest_framework import status


from django.db.models import Q

from amc.serializer import Scheme_Name_Mismatch_Serializer

from todo.serializers import AMCSerializer, SchemeSerializer

from amc.jobs.aum_process import start_process


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
    cats = Scheme.get_fund_categorization()

    types = []
    subtypes = []
    for key in cats:
        types.append(key)
        for row in cats[key]:
            subtypes.append(row["Text"])
    # ret = Scheme.objects.get_category_types()
    # return Response(ret)

    return Response(types)


@api_view()
def get_funds(request, type, sub_type):
    ret = Scheme.objects.get_funds(type=type, sub_type=sub_type)
    ser = SchemeSerializer(ret, many=True)
    return Response(ser.data)


@api_view()
def get_funds_amc(request, type, sub_type):
    """

    Returns the AMC based on schemes type and sub_type.

    """
    ret = Scheme.objects.get_funds(type=type, sub_type=sub_type)
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
        serial = AMCSerializer(resp, many=False)
        response.append(serial.data)
    return Response(response)


@api_view()
def get_funds_schemes(request, amc, type, sub_type):
    """

    Returns the Schemes based on schemes type and sub_type and amc.

    """
    ret = Scheme.objects.get_funds(amc=amc, type=type, sub_type=sub_type)
    ser = SchemeSerializer(ret, many=True)
    return Response(ser.data)


@api_view()
def get_funds_schemes_type(request, amc, type):
    """

    Returns the schemes based on schemes amc and type.

    """
    ret = Scheme.objects.get_funds(amc=amc, type=type)
    ser = SchemeSerializer(ret, many=True)
    return Response(ser.data)


@api_view()
def get_fund_subcategories(request, stype):
    # ret = Scheme.objects.get_sub_category_types(type)
    # return Response(ret)

    cats = Scheme.get_fund_categorization()

    subtypes = []
    for key in cats:
        if key == stype:
            for row in cats[key]:
                subtypes.append(row["Text"])

    return Response(subtypes)


class ListAmc(generics.ListAPIView):
    queryset = AMC.objects.all()
    serializer_class = AMCSerializer


class NameMismatchList(generics.ListAPIView):
    queryset = Scheme_Name_Mismatch.objects.all()
    serializer_class = Scheme_Name_Mismatch_Serializer


@api_view()
def get_probable_list_for_mismatch(request, amc):

    amc = AMC.objects.filter(name=amc).first()

    if amc:
        ret = Scheme.objects.raw(
            "SELECT * FROM `todo_scheme` WHERE amc_id = " + str(amc.id) + " and id not in (SELECT todo_scheme_info.scheme_id from todo_scheme_info)")
        ser = SchemeSerializer(ret, many=True)
        return Response(ser.data)
    else:
        return Response("amc not found" + amc, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view()
def fix_name_mismatch(request, mismatch_id, scheme_id):
    mismatchObj = Scheme_Name_Mismatch.objects.get(id=mismatch_id)
    name = getattr(mismatchObj, "name")
    scheme_category = getattr(mismatchObj, "category")
    scheme_sub_category = getattr(mismatchObj, "subcategory")

    Scheme.objects.filter(pk=scheme_id).update(
        fund_name=name,
        scheme_type=scheme_category, scheme_sub_type=scheme_sub_category)

    mismatchObj.delete()

    return Response()


@api_view()
def recalculate_mismatch():
    start_process()
    return Response()


@api_view()
def get_funds_without_category_or_sub_category(request):

    cats = Scheme.get_fund_categorization()

    types = []
    subtypes = []
    for key in cats:
        types.append(key)
        for row in cats[key]:
            subtypes.append(row["Text"])
            # print(row['Text'], "xxx", row['Value'])

    ret = Scheme.objects.exclude(
        Q(scheme_type__in=types) or Q(scheme_sub_type__in=subtypes))
    ser = SchemeSerializer(ret, many=True)
    return Response(ser.data)


@api_view()
def assign_fund_to_types(req, id, cat, subcat):
    Scheme.objects.filter(pk=id).update(
        scheme_type=cat, scheme_sub_type=subcat)
    return Response()


@api_view()
def delete_fund(req, id):

    # Scheme.objects.raw("delete FROM `amc_scheme_ter` where scheme_id = " + id)
    # Scheme.objects.raw(
    #     "delete from amc_scheme_portfolio_data where scheme_id " + id)
    # Scheme.objects.raw(
    #     "delete FROM `amc_scheme_aum` WHERE `scheme_id` = " + id)
    # Scheme.objects.raw(
    #     "delete FROM `stats_schemestats` WHERE `scheme_id` = " + id)
    # Scheme.objects.raw("delete FROM `todo_nav` where scheme_id = " + id)
    # Scheme.objects.raw(
    #     "DELETE FROM `todo_scheme` WHERE `todo_scheme`.`id` = " + id)

    Scheme.objects.filter(pk=id).update(fund_active=False)
    return Response()
