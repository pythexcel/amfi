
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from todo.models import AMC, Scheme, Nav, MFDownload
from todo.serializers import UserSerializer, AMCSerializer, SchemeSerializer, NavSerializer, MFDownloadSerializer

import requests
import datetime


def download_mf():
    print("Starting mf download")
    amc_id = 3
    count = MFDownload.objects.filter(
        amc_id=amc_id, has_data=False).count()

    print(count)

    if(count > 2):
        print("data completed for amc %s", amc_id)
        return

    days_gap = 30
    try:

        mfdownload = MFDownload.objects.filter(
            amc_id=amc_id).order_by('end_date').first()

        ser = MFDownloadSerializer(mfdownload)
        print(ser.data)
        if ser.data["amc_id"] is None:
            raise MFDownload.DoesNotExist('Record does not exist.')

        ser.data["start_date"] = "2019-03-27"
        ser.data["end_date"] = "2019-02-25"

        if ser.data["end_time"] is None and False:
            # this means previous script didn't run properly. so parsing it again
            # it dangenours can go in infite loop. better not do this for now
            start = ser.data["start_date"]
            start = datetime.datetime.strptime(
                start, '%Y-%m-%d')
            end = (start -
                   datetime.timedelta(days=days_gap))
        else:
            start = ser.data["end_date"]
            start = datetime.datetime.strptime(
                start, '%Y-%m-%d')
            end = (start -
                   datetime.timedelta(days=days_gap))

        # MFDownload.objects.filter(pk=mfdownload.id).update(start_date=start, end_date=end,
        #                   start_time=datetime.datetime.now(), end_time=None)

        mfdownload = MFDownload(
            amc_id=3, start_date=start, end_date=end, start_time=datetime.datetime.now())
        mfdownload.save()

    except MFDownload.DoesNotExist:
        start = datetime.date.today()
        end = (start -
               datetime.timedelta(days=days_gap))
        mfdownload = MFDownload(
            amc_id=3, start_date=start, end_date=end, start_time=datetime.datetime.now(), retry=0)
        mfdownload.save()

    url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf='+amc_id+'&tp=1&frmdt=' + \
        end.strftime("%d-%b-%Y")+'&todt='+start.strftime("%d-%b-%Y")

    print(start)
    print(end)

    res = do_process_data(url)

    if res is False:
        MFDownload.objects.filter(pk=mfdownload.id).update(
            end_time=datetime.datetime.now(), has_data=False)
    else:
        MFDownload.objects.filter(pk=mfdownload.id).update(
            end_time=datetime.datetime.now())

    print("Completed mf download")


def download_mf_input(amc_id, start, end):
    url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf='+amc_id+'&tp=1&frmdt=' + \
        end.strftime("%Y-%m-%d")+'&todt='+start.strftime("%Y-%m-%d")
    do_process_data(url)


amc_list = {}
scheme_list = {}


def fetch_or_save_amc(amc_name):
    if amc_name in amc_list:
        return amc_list[amc_name]
    try:
        amc = AMC.objects.get(name=amc_name)
    except AMC.DoesNotExist:
        amc = AMC(name=amc_name)
        amc.save()

    amc_list[amc_name] = amc
    return amc


def fetch_or_save_scheme(fund_code, amc, scheme_category, scheme_type, scheme_sub_type, fund_name, fund_option, fund_type):
    scheme_unique = fund_code + str(amc.id)
    if scheme_unique in scheme_list:
        return scheme_list[scheme_unique]
    try:
        scheme = Scheme.objects.get(
            fund_code=fund_code, amc=amc)
    except Scheme.DoesNotExist:
        scheme = Scheme(
            scheme_category=scheme_category,
            scheme_type=scheme_type,
            scheme_sub_type=scheme_sub_type,
            fund_code=fund_code,
            fund_name=fund_name,
            fund_option=fund_option,
            fund_type=fund_type,
            amc=amc
        )
        scheme.save()

    scheme_list[scheme_unique] = scheme
    return scheme


def do_process_data(url):
    print(url)
    response = requests.get(url)

    mf_nav_data = response.text.splitlines()

    colums = mf_nav_data[0].split(";")
    if colums[0] != "Scheme Code":
        print("no more data")

        print(url)

        return False

    amc_name = ""

    scheme_category = ""
    scheme_type = ""
    scheme_sub_type = ""

    for line in mf_nav_data[1:]:
        if len(line) > 0:
            if line.find(";") != -1:
                # df = pd.DataFrame(line.split(';'), index=colums)
                # print(df)
                mf_data = line.split(";")
                if len(mf_data[1].split("-")) == 3:
                    fund_name = mf_data[1].split("-")[0].strip()
                    fund_option = mf_data[1].split("-")[1].strip()
                    fund_type = mf_data[1].split("-")[2].strip()
                else:
                    if len(mf_data[1].split("-")) == 2:
                        fund_name = mf_data[1].split("-")[0].strip()
                        fund_option = ""
                        fund_type = mf_data[1].split("-")[1].strip()
                    else:
                        fund_name = mf_data[1].split("-")[0].strip()
                        fund_option = ""
                        fund_type = ""

                if fund_type == "Direct Plan" and fund_option == "Growth":
                    amc = fetch_or_save_amc(amc_name)


                    # print(mf_data[0])
                    

                    # ser = AMCSerializer(amc)
                    # print(ser.data)
                    scheme = fetch_or_save_scheme(
                        mf_data[0], amc, scheme_category, scheme_type, scheme_sub_type, fund_name, fund_option, fund_type)

                    # ser = SchemeSerializer(scheme)
                    # print(ser.data)

                    date_time_str = mf_data[7]
                    date_time_obj = datetime.datetime.strptime(
                        date_time_str, '%d-%b-%Y')

                    if mf_data[0] == "120564":
                        print(mf_data[4])
                        print(date_time_obj)
                        
                    try:
                        nav = Nav.objects.get(
                            date=date_time_obj, scheme=scheme)

                        ser = NavSerializer(nav)

                        if ser.data["nav"] != mf_data[4]:
                            Nav.objects.filter(
                                pk=nav.id).update(nav=mf_data[4])

                    except Nav.DoesNotExist:
                        nav = Nav(nav=mf_data[4],
                                  date=date_time_obj, scheme=scheme)
                        nav.save()

            else:
                if line.find(")") != -1:
                    x1 = line.find("(")
                    scheme_category = line[:x1].strip()
                    x1 = x1+1
                    scheme_type = line[x1:-1].split("-")[0].strip()
                    if len(line[x1:-1].split("-")) == 2:
                        scheme_sub_type = line[x1:-1].split("-")[1].strip()
                    else:
                        scheme_sub_type = ""

                    scheme_category = scheme_category
                    scheme_type = scheme_type
                    scheme_sub_type = scheme_sub_type
                else:
                    # print("amc")
                    # print(line.strip())
                    amc_name = line.strip()
                    pass

    return True


scheduler = BackgroundScheduler()

job = scheduler.add_job(download_mf, 'interval', minutes=1)

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
