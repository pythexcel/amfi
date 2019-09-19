from rest_framework.decorators import api_view
from rest_framework.response import Response

from rest_framework.views import APIView
from rest_framework import generics

from rest_framework import status

import json
from bson import json_util


import todo.logs


@api_view()
def get_critical_logs(request):

    logs = todo.logs.get_critical_logs()

    logs = [todo.logs.serialize_doc(log) for log in logs]

    return Response(json.dumps(logs, default=json_util.default))


@api_view()
def delete_log(request, log_id):
    todo.logs.clear_log(log_id)
    return Response()
