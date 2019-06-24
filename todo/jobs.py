
import logging
from apscheduler.schedulers.background import BackgroundScheduler

from todo.models import AMC, Scheme, Nav, MFDownload
from todo.serializers import UserSerializer, AMCSerializer, SchemeSerializer, NavSerializer, MFDownloadSerializer

import requests
import datetime


def download_mf():
    print("Starting mf download")
    days_gap = 30
    try:

        mfdownload = MFDownload.objects.filter(
            amc_id=3).order_by('end_date').first()
        ser = MFDownloadSerializer(mfdownload)
        print(ser.data)
        if ser.data["amc_id"] is None:
            raise MFDownload.DoesNotExist('Record does not exist.')

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

    response = requests.get(
        'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf=3&tp=1&frmdt='+end.strftime("%d-%b-%Y")+'&todt='+start.strftime("%d-%b-%Y"))

    mf_nav_data = response.text.splitlines()

    colums = mf_nav_data[0].split(";")
    if colums[0] != "Scheme Code":
        print("no more data")
        print(start)
        print(end)
        return

    amc_name = ""

    scheme_category = ""
    scheme_type = ""
    scheme_sub_type = ""

    print(start)
    print(end)

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
                    try:
                        amc = AMC.objects.get(name=amc_name)
                    except AMC.DoesNotExist:
                        amc = AMC(name=amc_name)
                        amc.save()

                    # ser = AMCSerializer(amc)
                    # print(ser.data)

                    try:
                        scheme = Scheme.objects.get(
                            fund_code=mf_data[0], amc=amc)
                    except Scheme.DoesNotExist:
                        scheme = Scheme(
                            scheme_category=scheme_category,
                            scheme_type=scheme_type,
                            scheme_sub_type=scheme_sub_type,
                            fund_code=mf_data[0],
                            fund_name=fund_name,
                            fund_option=fund_option,
                            fund_type=fund_type,
                            amc=amc
                        )
                        scheme.save()
                    # ser = SchemeSerializer(scheme)
                    # print(ser.data)

                    date_time_str = mf_data[7]
                    date_time_obj = datetime.datetime.strptime(
                        date_time_str, '%d-%b-%Y')

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
                    scheme_sub_type = line[x1:-1].split("-")[1].strip()

                    scheme_category = scheme_category
                    scheme_type = scheme_type
                    scheme_sub_type = scheme_sub_type
                else:
                    # print("amc")
                    # print(line.strip())
                    amc_name = line.strip()
                    pass

    MFDownload.objects.filter(pk=mfdownload.id).update(
        end_time=datetime.datetime.now())

    print("Completed mf download")

scheduler = BackgroundScheduler()

job = scheduler.add_job(download_mf, 'interval', minutes=1)

logging.basicConfig()
logging.getLogger('apscheduler').setLevel(logging.DEBUG)
