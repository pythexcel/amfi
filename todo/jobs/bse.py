import requests
import logging
import json
import datetime
import urllib.parse

import json

from todo.logs import startLogs, addLogs


from todo.models import Index, IndexData

# # These two lines enable debugging at httplib level (requests->urllib3->http.client)
# # You will see the REQUEST, including HEADERS and DATA, and RESPONSE with HEADERS but without DATA.
# # The only thing missing will be the response.body which is not logged.
# try:
#     import http.client as http_client
# except ImportError:
#     # Python 2
#     import httplib as http_client
# http_client.HTTPConnection.debuglevel = 1

# # You must initialize logging, otherwise you'll not see debug output.
# logging.basicConfig()
# logging.getLogger().setLevel(logging.DEBUG)
# requests_log = logging.getLogger("requests.packages.urllib3")
# requests_log.setLevel(logging.DEBUG)
# requests_log.propagate = True


bse_indexes = [
    "SENSEX",   
    "SPB15MIP", 
    "SPBSAIP",
    "SPBSEVIP",
    "SIBTEC",
    "BSE500",
    "BSE200",
    #"BSE100",
    "BSESML",
    "SI0800",
    "SI1000",
    "SIBANK",
    "SPBSE5S",
    "INFRA",
    "BSEMID",
    "SPB25XIP",
    "SPBSS5IP",
    "SPB25SIP",
    "SIBPSU"
]

        
# https://api.bseindia.com/BseIndiaAPI/api/ProduceCSVForDate/w?strIndex=SENSEX&dtFromDate=01/07/2019&dtToDate=02/04/2019
# https://api.bseindia.com/BseIndiaAPI/api/ProduceCSVForDate/w?strIndex=SENSEX&dtFromDate=01/07/2019&dtToDate=02/04/2019
#https://www.bseindia.com/markets/keystatics/Keystat_index.aspx
#https://www.bseindia.com/indices/IndexArchiveData.html

def process_bse_daily():
    log = startLogs("process_bse_daily", {})
    for name in bse_indexes:
        start_date = datetime.datetime.today()
        end_date = datetime.datetime.today() - datetime.timedelta(days=7)
        latest_index = Index.objects.get(name=name, type="BSE")
        process_data(name, start_date, end_date, latest_index, log)


def process_bse_historial():
    days = 90
    index = 0

    try:
        latest_index = Index.objects.get(parsed=False, type="BSE")
        # latest_index = Index.objects.filter(
        #     parsed=False).all().order_by("-end_date").first()
        name = latest_index.name
        start_date = getattr(latest_index, "end_date")
        end_date = start_date - datetime.timedelta(days=days)
    except Index.DoesNotExist:
        index = Index.objects.filter(type="BSE").all().count()
        if index >= len(bse_indexes):
            print("bse completed")
            return
        else:
            name = urllib.parse.quote(bse_indexes[index])
        start_date = datetime.datetime.today()
        end_date = datetime.datetime.today() - datetime.timedelta(days=days)
        latest_index = Index(
            name=urllib.parse.unquote(name),
            start_date=start_date,
            end_date=end_date,
            type="BSE"
        )
        latest_index.save()

    print(name)
    print(start_date)
    print(end_date)

    res = process_data(name, start_date, end_date, latest_index, False)

    if res:
        Index.objects.filter(pk=latest_index.id).update(
            start_date=start_date, end_date=end_date)
    else:
        Index.objects.filter(pk=latest_index.id).update(parsed=True)


def process_data(name, start_date, end_date, latest_index, log_id):

    params = {
        "fmdt": end_date.strftime("%d/%m/%Y"),
        "index": name,
        "period": "D",
        "todt": start_date.strftime("%d/%m/%Y")
    }
    url = "https://api.bseindia.com/BseIndiaAPI/api/IndexArchDaily/w"

    print(url)
    if log_id is not False:
        addLogs({
            "type": "log",
            "message": "URL: " + url
        }, log_id)

    response = requests.get(url, params=params)

    data = response.json()
    index_data = {}

    for row in data["Table"]:

        date = row["tdate"]
        open = row["I_open"]
        high = row["I_high"]
        low = row["I_low"]
        close = row["I_close"]
        index_data[date] = {
            "open": open,
            "high": high,
            "low": low,
            "close": close,
            "pe": row["I_pe"],
            "pe": row["I_pb"],
            "div": row["I_yl"]
        }

    if bool(index_data):
        for date in index_data:
            try:
                IndexData.objects.get(index=latest_index, date=datetime.datetime.strptime(
                    date, '%Y-%m-%dT%H:%M:%S'))
                # data exists nothing to do
            except IndexData.DoesNotExist:
                index_data_obj = IndexData(
                    index=latest_index,
                    date=datetime.datetime.strptime(
                        date, '%Y-%m-%dT%H:%M:%S'),
                    open=index_data[date]['open'],
                    close=index_data[date]['close'],
                    high=index_data[date]['high'],
                    low=index_data[date]['low'],
                    pe=index_data[date]['pe'] if 'pe' in index_data[date] else 0,
                    pb=index_data[date]['pb'] if 'pb' in index_data[date] else 0,
                    div=index_data[date]['div'] if 'div' in index_data[date] else 0
                )
                index_data_obj.save()
                if log_id is not False:
                    addLogs({
                        "type": "log",
                        "message": "saving data : " + json.dumps(index_data)
                    }, log_id)

        return True
    else:
        print("error in code")
        if log_id is not False:
            addLogs({
                "type": "error",
                "message": "problem parsing data"
            }, log_id)
        return False
