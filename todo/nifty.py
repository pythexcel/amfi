import requests
import logging
import json
import datetime
from bs4 import BeautifulSoup
import urllib.parse


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

# https://www.nseindia.com/products/dynaContent/equities/indices/historical_pepb.jsp?indexName=NIFTY%20NEXT%2050&fromDate=02-04-2018&toDate=01-07-2018&yield1=undefined&yield2=undefined&yield3=undefined&yield4=all
# https://www.nseindia.com/products/dynaContent/equities/indices/historical_pepb.jsp?indexName=NIFTY%20NEXT%2050&fromDate=02-Apr-2018&toDate=01-Jul-2018&yield1=undefined&yield2=undefined&yield3=undefined&yield4=all


def process_nifty():

    nifty_indexes = [
        "NIFTY NEXT 50",
        "NIFTY 50",
        "NIFTY SMLCAP 100",
        "NIFTY MIDCAP 100"
    ]

    bse_indexes = [
        "SENSEX"
    ]

    days = 90
    index = 0

    try:
        latest_index = Index.objects.get(parsed=False)
        # latest_index = Index.objects.filter(
        #     parsed=False).all().order_by("-end_date").first()
        name = latest_index.name
        start_date = getattr(latest_index, "end_date")
        # start_date = datetime.datetime.strptime(
        #     start_date, '%Y-%m-%d')
        # start_end = latest_index.end_date
        print(start_date)
        end_date = start_date - datetime.timedelta(days=days)
    except Index.DoesNotExist:
        index = Index.objects.filter().all().count()
        name = urllib.parse.quote(nifty_indexes[index])
        start_date = datetime.datetime.today()
        end_date = datetime.datetime.today() - datetime.timedelta(days=days)
        latest_index = Index(
            name=name,
            start_date=start_date,
            end_date=end_date
        )
        latest_index.save()

    print(name)
    print(start_date)
    print(end_date)

    url = "https://www.nseindia.com/products/dynaContent/equities/indices/historicalindices.jsp?indexType=" + \
        name+"&fromDate=" + \
        end_date.strftime("%d-%m-%Y")+"&toDate=" + \
        start_date.strftime("%d-%m-%Y")

    r = requests.get(url)

    print(url)

    url2 = "https://www.nseindia.com/products/dynaContent/equities/indices/historical_pepb.jsp?indexName=" + name+"&fromDate="+end_date.strftime("%d-%m-%Y")+"&toDate="+start_date.strftime(
        "%d-%m-%Y")+"&yield1=undefined&yield2=undefined&yield3=undefined&yield4=all"

    r2 = requests.get(url2)

    print(url2)

    # print(r.text)

    soup = BeautifulSoup(r.text, 'html.parser')
    csvContentDiv = soup.find("div", {"id": "csvContentDiv"})

    index_data = {}

    if csvContentDiv is not None:
        contents = csvContentDiv.contents
        for row in contents[0].split(":"):
            row = row.replace('"', "")
            cols = row.split(",")

            if (len(cols) > 5) & (cols[0] != "Date"):
                date = cols[0]
                open = cols[1]
                high = cols[2]
                low = cols[3]
                close = cols[4]
                index_data[date] = {
                    "open": open,
                    "high": high,
                    "low": low,
                    "close": close
                }

    else:

        table_body = soup.find("table")
        rows = table_body.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            if len(cols) > 5:
                date = cols[0]
                open = cols[1]
                high = cols[2]
                low = cols[3]
                close = cols[4]
                index_data[date] = {
                    "open": open,
                    "high": high,
                    "low": low,
                    "close": close
                }

    soup = BeautifulSoup(r2.text, 'html.parser')

    # print(r2.text)

    csvContentDiv = soup.find("div", {"id": "csvContentDiv"})

    if csvContentDiv is not None:

        contents = csvContentDiv.contents
        for row in contents[0].split(":"):
            row = row.replace('"', "")
            cols = row.split(",")

            if (len(cols) > 3) & (cols[0] != "Date"):
                date = cols[0]
                pe = cols[1]
                pb = cols[2]
                divyield = cols[3]

                index_data[date] = {
                    "open": open,
                    "high": high,
                    "low": low,
                    "close": close
                }

                if date in index_data:
                    index_data[date]["pe"] = pe
                    index_data[date]["pb"] = pb
                    index_data[date]["div"] = divyield

    else:

        table_body = soup.find("table")
        rows = table_body.find_all('tr')

        for row in rows:
            cols = row.find_all('td')
            cols = [ele.text.strip() for ele in cols]
            if len(cols) > 3:
                date = cols[0]
                pe = cols[1]
                pb = cols[2]
                divyield = cols[3]

                if date in index_data:
                    index_data[date]["pe"] = pe
                    index_data[date]["pb"] = pb
                    index_data[date]["div"] = divyield

    # print(index_data)

    # print(len(index_data))

    if bool(index_data):
        for date in index_data:
            try:
                print(date)
                IndexData.objects.get(index=latest_index, date=datetime.datetime.strptime(
                    date, '%d-%b-%Y'))
                # data exists nothing to do
            except IndexData.DoesNotExist:
                index_data_obj = IndexData(
                    index=latest_index,
                    date=datetime.datetime.strptime(
                        date, '%d-%b-%Y'),
                    open=index_data[date]['open'],
                    close=index_data[date]['close'],
                    high=index_data[date]['high'],
                    low=index_data[date]['low'],
                    pe=index_data[date]['pe'] if 'pe' in index_data[date] else 0,
                    pb=index_data[date]['pb'] if 'pb' in index_data[date] else 0,
                    div=index_data[date]['div'] if 'div' in index_data[date] else 0
                )
                index_data_obj.save()

        Index.objects.filter(pk=latest_index.id).update(
            start_date=start_date, end_date=end_date)
    else:
        Index.objects.filter(pk=latest_index.id).update(parsed=True)

    # print(rows)
    # print(soup.find_all("tr"))

    return

    #         "https://api.bseindia.com/BseIndiaAPI/api/ProduceCSVForYear/w?strIndex=SENSEX&dtFromDate=01/01/2019&dtToDate=01/07/2019"

    # url = "https://www.niftyindices.com/Backpage.aspx/getHistoricaldatatabletoString"

    # params = {
    #     'name': 'NIFTY 50',
    #     'startDate': '01-Jul-2018',
    #     'endDate': '01-Jul-2019'
    # }

    # response = requests.post(url, json=params)

    # data = response.json()

    # # print(data["d"])

    # d = json.loads(data["d"])

    # for line in d:
    # print(line)
    # line["Index Name"]
    # line["INDEX_NAME"]
    # line["HistoricalDate"]
    # line["OPEN"]
    # line["HIGH"]
    # line["LOW"]
    # line["CLOSE"]

    # date = datetime.datetime.strptime(
    #     line["HistoricalDate"], '%d %b %Y')

    # try:
    #     index_data = Index.objects.get(
    #         trade_name=line["INDEX_NAME"], date=date)
    # except Index.DoesNotExist:
    #     index_data = Index(
    #         name=line["Index Name"],
    #         trade_name=line["INDEX_NAME"],
    #         date=date,
    #         open=open,
    #         close=close)
    #     index_data.save()

    return True
    # print(data)
