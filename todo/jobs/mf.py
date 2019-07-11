from todo.models import AMC, Scheme, Nav, MFDownload, NavSerializer
from todo.serializers import UserSerializer, AMCSerializer, SchemeSerializer, MFDownloadSerializer


import requests
import datetime

amc_no_start = 1
amc_no_end = 75


def find_amc_no_to_process():
    # on amfi website all amc have different no and they are not in serial order.
    # so we need to keep checkin amc's until we get data and skip if data not found

    if AMC.objects.all().count() > 0:
        try:
            amc = AMC.objects.get(parsed=False)
            # this mean there is an amc which still has data being parsed
            # so simply continue with that
            ser = AMCSerializer(amc)
            amc_no = ser.data["amc_no"]
            amc_id = amc.id
        except AMC.DoesNotExist:
            # if there is no amc being parsed then need to find the
            # last amc i.e amc which max amc_no
            amc = AMC.objects.all().order_by("-amc_no").first()
            ser = AMCSerializer(amc)
            print(ser.data)
            if ser.data["next_amc_no"] == 0:
                amc_no = int(ser.data["amc_no"])+1
            else:
                amc_no = int(ser.data["next_amc_no"])+1

            # above if condition is due to a problem that all amc_no are not in sequence
            # e.g after amc no 5 there is no amc with no 6 rather to 7.
            # because our code works only incrementally and to solve this problem have added
            # another db column next_amc_no which stores these increments where amc no is missing

            AMC.objects.filter(pk=amc.id).update(next_amc_no=amc_no)
            amc_id = -1
            if amc_no > amc_no_end:
                print("all amcs completed")
                return 9999, 9999

    else:
        # this mean there is no amc is db.
        # db is fully empty so start from 1
        amc_no = amc_no_start

    return amc_no, amc_id


def download_mf_historical_data():
    print("Starting mf download")

    amc_no, amc_id = find_amc_no_to_process()

    if amc_no == 9999:
        print("all amcs completed!")
        return

    print("checking for amc no ", amc_no)

    if amc_id != -1:
        # if amc_id is -1 this means this is a new amc. so nothing to update or check
        count = MFDownload.objects.filter(
            amc_id=amc_id, has_data=False).count()

        if(count > 2):
            # this means we didn't find data when parsing url to consicutive times
            # which means for sure amc data is finished
            print("data completed for amc %s", amc_no)
            AMC.objects.filter(amc_no=amc_no).update(parsed=True)
            return

    days_gap = 90
    try:

        mfdownload = MFDownload.objects.filter(
            amc_id=amc_id).order_by('end_date').first()

        ser = MFDownloadSerializer(mfdownload)

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
            amc_id=amc_id, start_date=start, end_date=end, start_time=datetime.datetime.now())
        mfdownload.save()

    except MFDownload.DoesNotExist:
        start = datetime.date.today()
        end = (start -
               datetime.timedelta(days=days_gap))
        mfdownload = MFDownload(
            amc_id=amc_id, start_date=start, end_date=end, start_time=datetime.datetime.now(), retry=0)
        mfdownload.save()

    url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf='+str(amc_no)+'&tp=1&frmdt=' + \
        end.strftime("%d-%b-%Y")+'&todt='+start.strftime("%d-%b-%Y")

    print(start)
    print(end)

    res = do_process_data(url, amc_no)

    if res is False:
        # data didn't come from amfi url which menas false
        MFDownload.objects.filter(pk=mfdownload.id).update(
            end_time=datetime.datetime.now(), has_data=False)
    else:
        # data came we are just update the end time
        MFDownload.objects.filter(pk=mfdownload.id).update(
            end_time=datetime.datetime.now())

    print("Completed mf download")


def download_mf_input(amc_id, start, end):
    url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?mf='+str(amc_id)+'&tp=1&frmdt=' + \
        end.strftime("%Y-%m-%d")+'&todt='+start.strftime("%Y-%m-%d")
    do_process_data(url, amc_id)


def schedule_daily_download_mf():
    date = datetime.date.today()
    url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt=' + \
        date.strftime("%Y-%m-%d")
    do_process_data(url, -1)
    date = datetime.date.today() - datetime.timedelta(days=1)
    url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt=' + \
        date.strftime("%Y-%m-%d")
    do_process_data(url, -1)
    date = datetime.date.today() - datetime.timedelta(days=2)
    url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt=' + \
        date.strftime("%Y-%m-%d")
    do_process_data(url, -1)


def download_mf_input_date(date):
    # process mf data only for a single day for all mfs
    # url = 'http://portal.amfiindia.com/DownloadNAVHistoryReport_Po.aspx?frmdt=' + \
        # date.strftime("%Y-%m-%d")
    url = "https://www.amfiindia.com/spages/NAVAll.txt?t=" + \
        date.strftime("%Y%m%d000000")
    do_process_data(url, -1)


amc_list = {}
scheme_list = {}


def fetch_amc(amc_name):
    if amc_name in amc_list:
        return amc_list[amc_name]

    try:
        amc = AMC.objects.get(name=amc_name)
        amc_list[amc_name] = amc
        return amc
    except AMC.DoesNotExist:
        return False


def fetch_or_save_amc(amc_name, amc_no):
    # this will cache amc name and we don't need to alwways fire sql query
    if amc_name in amc_list:
        return amc_list[amc_name]
    try:
        amc = AMC.objects.get(name=amc_name)
    except AMC.DoesNotExist:
        if amc_no != -1:
            amc = AMC(name=amc_name, amc_no=amc_no)
            amc.save()

    amc_list[amc_name] = amc
    return amc


def fetch_or_save_scheme(fund_code, amc, scheme_category, scheme_type, scheme_sub_type, fund_name, fund_option, fund_type):
    # this will cache scheme and we don't need to alwways fire sql query
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


def do_process_data(url, amc_no):
    print(url)
    response = requests.get(url)

    mf_nav_data = response.text.splitlines()

    scheme_code_index = 0
    scheme_name_index = 1
    nav_index = 4
    date_index = 7

    colums = mf_nav_data[0].split(";")

    try:
        scheme_code_index = colums.index("Scheme Code")
        scheme_name_index = colums.index("Scheme Name")
        nav_index = colums.index("Net Asset Value")
        date_index = colums.index("Date")
    except ValueError:
        print("no more data")
        print(url)
        return False

    amc_name = ""

    print("valid data found", len(mf_nav_data))

    scheme_category = ""
    scheme_type = ""
    scheme_sub_type = ""

    for line in mf_nav_data[1:]:
        if len(line.strip()) > 0:
            # print(line)
            if line.find(";") != -1:
                # df = pd.DataFrame(line.split(';'), index=colums)
                # print(df)
                mf_data = line.split(";")
                if len(mf_data[scheme_name_index].split("-")) == 3:
                    fund_name = mf_data[scheme_name_index].split(
                        "-")[0].strip()
                    fund_option = mf_data[scheme_name_index].split(
                        "-")[1].strip()
                    fund_type = mf_data[scheme_name_index].split(
                        "-")[2].strip()
                else:
                    if len(mf_data[scheme_name_index].split("-")) == 2:
                        fund_name = mf_data[scheme_name_index].split(
                            "-")[0].strip()
                        fund_option = ""
                        fund_type = mf_data[scheme_name_index].split(
                            "-")[1].strip()
                    else:
                        fund_name = mf_data[scheme_name_index].split(
                            "-")[0].strip()
                        fund_option = ""
                        fund_type = ""

                # print(fund_type)
                # print(fund_option)

                # print("Direct" in line)
                # print("Growth" in line)

                if "Direct" in line:
                    fund_type = "Direct"
                else:
                    fund_type = "Regular"

                if "Growth" in line:
                    fund_option = "Growth"

                if fund_type == "Direct" and fund_option == "Growth":

                    if amc_no == -1:
                        amc = fetch_amc(amc_name)
                        if amc == False:
                            print("amc name doesn't exist ", amc_name)
                            continue
                    else:
                        amc = fetch_or_save_amc(amc_name, amc_no)

                    # print(mf_data[0])

                    print("saving to db ", line)

                    # ser = AMCSerializer(amc)
                    # print(ser.data)
                    scheme = fetch_or_save_scheme(
                        mf_data[scheme_code_index], amc, scheme_category, scheme_type, scheme_sub_type, fund_name, fund_option, fund_type)

                    # ser = SchemeSerializer(scheme)
                    # print(ser.data)

                    date_time_str = mf_data[date_index]
                    date_time_obj = datetime.datetime.strptime(
                        date_time_str, '%d-%b-%Y')

                    try:
                        nav = Nav.objects.get(
                            date=date_time_obj, scheme=scheme)

                        ser = NavSerializer(nav)

                        if ser.data["nav"] != mf_data[nav_index]:
                            Nav.objects.filter(
                                pk=nav.id).update(nav=mf_data[nav_index])

                    except Nav.DoesNotExist:
                        nav = Nav(nav=mf_data[nav_index],
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
                    print("amc")
                    print(line.strip())
                    amc_name = line.strip()
                    pass

    return True
