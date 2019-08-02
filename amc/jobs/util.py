from fuzzywuzzy import fuzz, process
import datefinder
import re
import pandas as pd
import datetime
from pyxlsb import open_workbook

import os

import zipfile
import shutil
from subprocess import call

from todo.models import AMC


local_base_path = "/mnt/c/work/newdref/"
server_base_path = "/home/node/manish_test_mf/"


dir_path = os.path.dirname(os.path.realpath(__file__))

actual_path = server_base_path

if local_base_path in dir_path:
    actual_path = local_base_path


portfolio_path = actual_path + "mf_portfolio_download"
ter_path = actual_path + "mf_ter_download"
aum_path = actual_path + "mf_aum_download"
download_path = actual_path + "downloads"


def generic_process_zip_file(base_folder_path):
    for (dirpath, dirnames, filenames) in os.walk(base_folder_path):
        for f in filenames:
            if ".xlsb" in f:
                print("process xlsb ", f)
                call(["soffice", "--headless", "--convert-to", "xlsx", os.path.join(
                    base_folder_path, f), "--outdir", base_folder_path])
                try:
                    os.mkdir(os.path.join(
                        base_folder_path, "processed_xlsb"))
                except FileExistsError:
                    pass

                os.rename(os.path.join(base_folder_path, f), os.path.join(
                    os.path.join(base_folder_path, "processed_xlsb"), f))

            if ".zip" in f:

                print("processing file ", f)
                with zipfile.ZipFile(os.path.join(base_folder_path, f)) as zip_file:
                    for member in zip_file.namelist():
                        filename = os.path.basename(member)
                        # skip directories
                        if not filename:
                            continue

                        # copy file (taken from zipfile's extract)
                        source = zip_file.open(member)
                        target = open(os.path.join(
                            base_folder_path, filename), "wb")
                        with source, target:
                            shutil.copyfileobj(source, target)

                with zipfile.ZipFile(os.path.join(base_folder_path, f), "r") as zip_ref:
                    print(base_folder_path)
                    zip_ref.extractall(base_folder_path)
                # os.remove(os.path.join(path, f))
                try:
                    os.mkdir(os.path.join(base_folder_path, "processed"))
                except FileExistsError:
                    pass

                os.rename(os.path.join(base_folder_path, f), os.path.join(
                    os.path.join(base_folder_path, "processed"), f))

        break  # this break is important to prevent further processing of sub directories


def read_excel(xls, sheet_name):
    # this is a generic function to read both xlsb file and xls file
    # for xlsb file we need a seperate module
    try:
        if "wb" in xls:
            return xls[sheet_name]
    except:
        return pd.read_excel(xls, sheet_name)


def ExcelFile(path):
    # this is a generic function to read both xlsb file and xls file
    # for xlsb file we need a seperate module
    if ".xlsb" in path:
        print("reading xlsb file")
        wb = False
        ret = {}
        with open_workbook(path) as wb:
            sheets = wb.sheets
            i = 0
            for sheet_name in sheets:
                with wb.get_sheet(sheet_name) as sheet:
                    df = []
                    for row in sheet.rows():
                        df.append([item.v for item in row])

                    df = pd.DataFrame(df[1:], columns=df[0])
                    ret[sheet_name] = df
                    ret[i] = df
                    i += 1

        ret["wb"] = wb
        ret["sheet_names"] = wb.sheets
        return ret
    else:
        try:
            return pd.ExcelFile(path)
        except Exception as e:
            print(e)
            df = pd.read_html(path)
            print(df)
            return df


def get_amc_common_names():
    amc_names = []
    for amc in AMC.objects.all():
        name = amc.name
        name = name.replace("Mutual Fund", "").strip()
        name = name.replace("Financial", "").strip()  # for jm financial
        name = name.replace("Templeton", "").strip()  # for franklin
        name = name.replace("Aditya", "").strip()  # for absl

        name2 = name.replace("Mahindra", "").strip()  # for kotak mahindra

        if not name2.strip():
            # this is mahindra mutual fund
            pass
        else:
            name = name2

        if "PPFAS" in name:
            name = "Parag Parikh"

        # we can also try another logic i.e finding the common word among all fund names
        # instead of removing above manually. but will see that later on
        amc_names.append(name)

    amc_names.append("escorts")
    # quant mf aquired escrots so there older portfolio have name escorts

    return amc_names


def find_row_with_isin_heading(df, scheme):
    # most of our logic is based on isin row.
    # this row is most important is present in all excel sheet
    # generally data above isin row has generic fund informatino like scheme name, date etc
    # and below the isin has fund portfolio like isin no etc

    expected_cols = ["Name", "ISIN", "Quantity", "Coupon",
                     "Rating", "Industry", "Market", "NAV", "Assets", "AUM"]

    # for col in expected_cols:
    mask = df.apply(lambda x: x.astype(str).str.contains('ISIN', False))
    df1 = df[mask.any(axis=1)]
    indexes = df1.index.values

    col_indexes = {}

    if len(indexes) > 0:
        index = indexes[0]
        base_row_index = index

        col_indexes["row_index"] = base_row_index

        base_row = df.iloc[index].to_numpy()

        indexes = []
        for col in expected_cols:
            for val in base_row:
                ratio = fuzz.token_set_ratio(col, val)
                # print(ratio, "==", col, val)
                if ratio > 95:
                    i = list(base_row).index(val)
                    col_indexes[col] = i
                    indexes.append(i)
                    break

        col_indexes["indexes"] = indexes

    if "Rating" in col_indexes and "Industry" in col_indexes:
        del col_indexes["Industry"]

    if "Industry" in col_indexes:
        col_indexes["Rating"] = col_indexes["Industry"]
        del col_indexes["Industry"]

    if "NAV" in col_indexes and "Assets" in col_indexes:
        del col_indexes["Assets"]

    if "Assets" in col_indexes:
        col_indexes["NAV"] = col_indexes["Assets"]
        del col_indexes["Assets"]

    if "AUM" in col_indexes:
        col_indexes["NAV"] = col_indexes["AUM"]
        del col_indexes["AUM"]

    print(col_indexes)
    return col_indexes
    # print(df1)


def find_date_from_sheet(df, file_name=False):
    # trying to find date from sheet. logic mainly depends on "As on" which is mentioned in every sheet
    # so trying to identity which cell has "as on" mentioned and then find date in that cell

    # for some amc i don't remember name it didn't have as on, rather it had "month ended"

    df.loc[-1] = df.columns
    df.index = df.index + 1
    df = df.sort_index()

    # print(df)
    mask = df.apply(lambda x: x.astype(
        str).str.contains('as on|month ended|month of', False))
    df1 = df[mask.any(axis=1)]
    df1 = df1.fillna(0)
    # print("date finding ")
    # print(df1)

    cells = []

    # for cell in df1.columns:
    #     if cell != 0:
    #         cells.append(cell)

    for row in df1.to_numpy():
        for cell in row:
            if cell != 0:
                cells.append(cell)

    if file_name != False:
        cells.append("as on" + file_name)

    date_matched = False
    year = ""
    matches = []

    for cell in cells:
        if isinstance(cell, pd._libs.tslibs.timestamps.Timestamp):
            print(cell)
            date_matched = cell.to_pydatetime()
            break

        if "month of" in str(cell) or "as on" in str(cell) or "for the month ended" in str(cell):
            # print(cell)
            try:
                cell = cell[cell.index("as on")+len("as on"):]
            except:
                try:
                    cell = cell[cell.index(
                        "for the month ended")+len("for the month ended"):]
                except:
                    cell = cell[cell.index(
                        "month of")+len("month of"):]

            r = re.compile('(?<!\d)(?:2100|200[1-9]|20[1-9]\d)(?!\d)')
            match = re.search(r, cell)
            if match is not None:
                # print(match.group())
                year = match.group()

                print(cell)
                matches = datefinder.find_dates(cell)
                for match in matches:
                    if match.strftime("%Y") == year:
                        date_matched = match

                if date_matched is False:
                    # if date finder is not able to find for some reaosn
                    # doing text match with all months possible
                    for i in range(12):
                        d = datetime.date(int(year), (i+1), 1)
                        # print(d)
                        cell = cell.replace(year, "")
                        if d.strftime("%b") in cell or d.strftime("%B") in cell or d.strftime("%m") in cell:
                            print(d)
                            date_matched = d
                            break

    print("trying to find date", date_matched)

    if date_matched == False:
        print("date not found at all")
        print(df1)
        print("year found ", year)
        for match in matches:
            print("date matches ", match)

    else:
        if date_matched.strftime("%Y") not in ["2015", "2016", "2017", "2018", "2019"]:
            print("date found but somthing went wrong need to analytize")
            print(df1)
            print("year found ", match)
            for match in matches:
                print("date matches ", match)
            return False

    return date_matched


def find_date_from_filename(filename):
    # this will match only year/month not actual date
    # use this as last resort if normal functon don't work

    years = [2016, 2017, 2018, 2019, 2020, 2021]

    dateFound = False

    for year in years:
        d = datetime.date(int(year), 1, 1)
        if d.strftime("%y") in filename or d.strftime("%Y") in filename:
            for i in range(12):
                d = datetime.date(int(year), (i+1), 1)
                # print(d)
                if d.strftime("%b").lower() in filename.lower() or d.strftime("%B").lower() in filename.lower() or d.strftime("%m") in filename.lower():
                    print(d)
                    dateFound = d
                    break
            break

    return dateFound
# this function is to find the fund name from sheet.


def match_fund_name_from_sheet(fund_names, sheet_df):

    # for col in expected_cols:
    mask = sheet_df.apply(lambda x: x.astype(str).str.contains('ISIN', False))
    df1 = sheet_df[mask.any(axis=1)]
    indexes = df1.index.values

    if len(indexes) > 0:
        index = indexes[0]
        df1 = sheet_df.head(index)
    else:
        df1 = df1.head(3)

    df1 = df1.fillna(0)

    # print(df1)
    # print(df1.to_numpy()
    # print(len(df1.to_numpy()))

    cells = []

    for cell in df1.columns:
        if cell != 0:
            cells.append(cell)
            # print(cell)

    for row in df1.to_numpy():
        for cell in row:
            if cell != 0:
                cells.append(cell)
                # print(cell)

    # string = df1.to_string()

    max_score = 0
    final_match = None

    for fund_name in fund_names:
        for cell in cells:
            ratio = fuzz.token_set_ratio(fund_name, cell)
            if ratio > 95:
                if ratio > max_score:
                    max_score = ratio
                    final_match = fund_name

                # print(fund_name, cell)
                # print(ratio)

    if final_match is None:
        print("fund not found here is info to debug")
        print(df1)

    return final_match, max_score


# def download_portfolio_from_website():
# tried this option but doesn;t look fesable.
# facing different isses with parsing data. since this is once a month operation maybe
# better to do it manually at this stage.
#     download_list = {}

#     # https://mutualfund.adityabirlacapital.com:443/-/media/bsl/files/resources/monthly-portfolio/monthly-portfolio-june-2018-rev.zip
#     # https://mutualfund.adityabirlacapital.com/-/media/bsl/files/resources/monthly-portfolio/sebi_monthly_portfolio-jan-19.zip
#     # https://mutualfund.adityabirlacapital.com/-/media/bsl/files/resources/monthly-portfolio/monthly-portfolio-march-2018.zip
#     # https://mutualfund.adityabirlacapital.com/-/media/bsl/files/resources/monthly-portfolio/monthly-portfolio-september-2018.zip
#     # https://mutualfund.adityabirlacapital.com/-/media/bsl/files/resources/monthly-portfolio/monthly-portfolio-february-2019.zip
#     # https://mutualfund.adityabirlacapital.com:443/-/media/bsl/files/resources/monthly-portfolio/monthly-portfolio-january-2017.zip
#     # download_list["Aditya Birla Sun Life Mutual Fund"] = [
#     #     "https://mutualfund.adityabirlacapital.com:443/-/media/bsl/files/resources/monthly-portfolio/monthly-portfolio-%B-%Y.zip",
#     #     "https://mutualfund.adityabirlacapital.com:443/-/media/bsl/files/resources/monthly-portfolio/monthly-portfolio-%b-%Y.zip",
#     #     "https://mutualfund.adityabirlacapital.com:443/-/media/bsl/files/resources/monthly-portfolio/sebi_monthly_portfolio-%B-%y.zip",
#     #     "https://mutualfund.adityabirlacapital.com:443/-/media/bsl/files/resources/monthly-portfolio/sebi_monthly_portfolio-%b-%y.zip",
#     #     "https://mutualfund.adityabirlacapital.com:443/-/media/bsl/files/resources/monthly-portfolio/monthly-portfolio-%B-%Y-rev.zip",
#     #     "https://mutualfund.adityabirlacapital.com:443/-/media/bsl/files/resources/monthly-portfolio/monthly-portfolio-%b-%Y-rev.zip",
#     #     "https://mutualfund.adityabirlacapital.com:443/-/media/bsl/files/resources/monthly-portfolio/monthly-portfolio-%B-%y-rev.zip",
#     #     "https://mutualfund.adityabirlacapital.com:443/-/media/bsl/files/resources/monthly-portfolio/monthly-portfolio-%b-%y-rev.zip"
#     # ]
#     # download_list["DSP Mutual Fund"] = [
#     #     "https://www.dspim.com/docs/default-source/portfolio-disclosures/month_end_portfolio_disclosure_%b%Y.zip?sfvrsn=2"
#     # ]

#     download_list["HDFC Mutual Fund"] = [
#         "https://files.hdfcfund.com/s3fs-public/%Y-%m/Monthly%20Portfolios%20for%20%b%20%Y_0.xls",
#         "https://files.hdfcfund.com/s3fs-public/%Y-%m/Monthly%20Portfolios%20for%20%b%20%Y_1.xls"
#     ]

#     years = [2019, 2018]

#     for amc in download_list:
#         urls = download_list[amc]

#         for i in range(11):
#             for year in years:
#                 month = i + 1
#                 # month_str = datetime.date(year, month, 1).strftime('%B')
#                 # print(month_str)

#                 found = False
#                 for url in urls:
#                     if "%Y" in url:
#                         url = url.replace("%Y", str(year))

#                     if "%y" in url:
#                         url = url.replace("%y", datetime.date(
#                             year, month, 1).strftime('%y'))

#                     if "%b" in url:
#                         month_str = datetime.date(
#                             year, month, 1).strftime('%b').lower()
#                         url = url.replace("%b", month_str)

#                     if "%B" in url:
#                         month_str = datetime.date(
#                             year, month, 1).strftime('%B').lower()
#                         url = url.replace("%B", month_str)

#                     if "%m" in url:
#                         month_str = datetime.date(
#                             year, month, 1).strftime('%m').lower()
#                         url = url.replace("%m", month_str)

#                     print(url)
#                     h = requests.head(url, allow_redirects=True, verify=False)
#                     # print(h.status_code)


#                     if h.status_code == 200:
#                         found = True

#                         # try:
#                         #     port_url = Scheme_Portfolio.objects.get(
#                         #         amc=amc,
#                         #         year=year,
#                         #         month=month
#                         #     )
#                         #     Scheme_Portfolio.objects.filter(
#                         #         pk=port_url.id, url=url)
#                         # except Scheme_Portfolio.DoesNotExist:
#                         #     port_url = Scheme_Portfolio_Url(
#                         #         amc=amc,
#                         #         year=year,
#                         #         month=month,
#                         #         url=url
#                         #     )
#                         #     port_url.save()

#             if found == False:
#                 print("no url found for year ", year, " and month ", month)
