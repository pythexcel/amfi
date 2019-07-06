import pandas as pd
import numpy as np
import requests

import datetime
from fuzzywuzzy import fuzz, process

from todo.models import Scheme, AMC, Scheme_Portfolio, Scheme_Portfolio_Url

import datefinder
import zipfile
import os
import re
import traceback
import shutil
from pyxlsb import open_workbook


path = "/mnt/c/work/newdref/restapi/mf_portfolio_download"


"""

# https://mutualfund.adityabirlacapital.com/forms-and-downloads/portfolio
# https://www.icicipruamc.com/Downloads/MonthlyPortfolioDisclosure.aspx

# https://www.dspim.com/about-us/mandatory-disclosure/month-end-portfolio-disclosures

https://www.hdfcfund.com/statutory-disclosure/monthly-portfolio

https://www.barodamf.com/Downloads/Pages/Latest-Factsheet-and-Profile.aspx

https://www.principalindia.com/all-downloads/disclosures

http://www.quant-mutual.com/statutory-disclosures

https://www.jmfinancialmf.com/Downloads/FactSheets.aspx?SubReportID=A49C5853-C27A-42C5-9703-699AFEACE164

https://assetmanagement.kotak.com/portfolios

https://www.licmf.com/statutory-disclosure

https://www.reliancemutual.com/investor-service/downloads/factsheets

https://www.sbimf.com/en-us/portfolios

https://www.tatamutualfund.com/downloads/monthly-portfolio

https://www.taurusmutualfund.com/Download/portfolio.php

https://www.franklintempletonindia.com/investor/reports

https://www.utimf.com/about/statutory-disclosures/scheme-dashboard

https://www.canararobeco.com/statutory-disclosures/scheme-monthly-portfolio#

https://www.sundarammutual.com/Monthly_Portfolio

http://www.saharamutual.com/Downloads/MonthlyPortfolio.aspx

"""

# need to figure out multiple things in this
# 1. how to download different excel sheets from diffrent mf providers
# 2. need some kind of error report if portfolio import fails
# 3. there are multiple funds like bharatcon serial1, 2, 3 etc need to see how to fix this
# 4. need to be able to find out if for certain funds portfolio was not import or for full house


def read_excel(xls, sheet_name):
    try:
        if "wb" in xls:
            return xls[sheet_name]
    except:
        return pd.read_excel(xls, sheet_name)


def ExcelFile(path):
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
        return pd.ExcelFile(path)


def process_data():

    process_zip_file()
    identify_amc()
    return
    # download_portfolio_from_website()
    # return

    # print(df1)

    xls = ExcelFile(
        '/mnt/c/work/newdref/restapi/mf_portfolio_download/Aditya Birla Sun Life Mutual Fund/Monthly-Portfolio-April-2018.xlsx')

    # amc = "Aditya Birla Sun Life Mutual Fund"

    amc = "Aditya Birla Sun Life Mutual Fund"

    amc = AMC.objects.get(name=amc)
    # amc_id = amc.id

    schemes = Scheme.objects.filter(amc=amc)

    fund_names = {}

    for scheme in schemes:
        fund_name = getattr(scheme, "fund_name")
        fund_names[fund_name] = scheme
        print(fund_name)

    try:
        sheet_names = xls["sheet_names"]
    except:
        sheet_names = xls.sheet_names

    for sheet_name in sheet_names:
        if sheet_name == "Index":
            continue
        print("checking for sheet name", sheet_name)
        df1 = pd.read_excel(xls, sheet_name)

        fund, ratio = match_fund_name_from_sheet(fund_names.keys(), df1)

        print(fund, "===",  ratio, "===", sheet_name)

        if fund is not None:
            col_indexes = find_row_with_isin_heading(df1, fund_names[fund])

            scheme = fund_names[fund]

            print(fund)

            return

            if "ISIN" in col_indexes and "Name" in col_indexes and "Market" in col_indexes and "Quantity" in col_indexes and "Rating" in col_indexes:
                # df1.fillna(False)
                # df1.rename()

                columns = [""] * df1.shape[1]

                print(columns)
                for key in col_indexes:
                    if key != "row_index" and key != "indexes":
                        idx = col_indexes[key]
                        columns[idx] = key

                print(columns)

                df1.columns = columns

                print(df1.iloc[col_indexes["row_index"]
                      :, col_indexes["indexes"]])

                df2 = df1.iloc[(col_indexes["row_index"]+1)
                                :, col_indexes["indexes"]]
                df2 = df2.fillna(False)

                if "Coupon" not in df2.columns:
                    df2["Coupon"] = 0

                for row in df2.itertuples():
                    name = row.Name
                    isin = row.ISIN
                    quantity = row.Quantity
                    coupon = row.Coupon
                    rating = row.Rating
                    market = row.Market
                    nav_per = row.NAV

                    if name == False:
                        # simply skip data
                        continue

                    if isin != False:
                        # this is some kind of security either bond or stock

                        if coupon != False:
                            # this is debt fund

                            scheme_portfolio = Scheme_Portfolio(
                                name=name,
                                isin=isin,
                                quantity=quantity,
                                coupon=coupon,
                                rating=rating,
                                market=market,
                                percent=nav_per
                            )
                            # scheme_portfolio.save()

                        else:
                            # this is stock
                            scheme_portfolio = Scheme_Portfolio(
                                name=name,
                                isin=isin,
                                quantity=quantity,
                                industry=rating,
                                market=market,
                                percent=nav_per
                            )
                            # scheme_portfolio.save()

                    else:
                        if quantity != False and rating != False:
                            # looks like unlisted stock or bond
                            if coupon != False:
                                scheme_portfolio = Scheme_Portfolio(
                                    name=name,
                                    quantity=quantity,
                                    coupon=coupon,
                                    rating=rating,
                                    market=market,
                                    percent=nav_per
                                )
                                # scheme_portfolio.save()
                            else:
                                scheme_portfolio = Scheme_Portfolio(
                                    name=name,
                                    quantity=quantity,
                                    industry=rating,
                                    market=market,
                                    percent=nav_per
                                )
                                # scheme_portfolio.save()
                        else:
                            # this is general classification. not saving this for now
                            pass

                    print(name)

                print("columns present")
                #
            else:
                print("unable to read data key columns missing")

        break

    # print(df1)

    return

    # print(fund_names)

    # print(string)

    # xls = pd.ExcelFile('/mnt/c/work/newdref/restapi/Monthly-Portfolio-May-2019.xls')
    # df1 = pd.read_excel(xls, 0)
    # print(df1)


def find_row_with_isin_heading(df, scheme):

    # if scheme.is_debt():
    expected_cols = ["Name", "ISIN", "Quantity", "Coupon",
                     "Rating", "Industry", "Market", "NAV", "Assets"]
    # else:
    #     if scheme.is_equity():
    #         expected_cols = ["Name", "ISIN",
    #                          "Quantity", "Industry", "Market", "NAV", "Assets"]
    #     else:
    #         expected_cols = ["Name", "ISIN", "Quantity", "Coupon",
    #                          "Rating", "Industry", "NAV Assets"]

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

    print(col_indexes)
    return col_indexes
    # print(df1)


def process_zip_file():
    # many mf have portfolio as zip files so first we need to extract them

    for (dirpath, dirnames, filenames) in os.walk(path):
        for f in filenames:
            if ".zip" in f:

                print("processing file ", f)
                with zipfile.ZipFile(os.path.join(path, f)) as zip_file:
                    for member in zip_file.namelist():
                        filename = os.path.basename(member)
                        # skip directories
                        if not filename:
                            continue

                        # copy file (taken from zipfile's extract)
                        source = zip_file.open(member)
                        target = open(os.path.join(path, filename), "wb")
                        with source, target:
                            shutil.copyfileobj(source, target)

                with zipfile.ZipFile(os.path.join(path, f), "r") as zip_ref:
                    print(path)
                    zip_ref.extractall(path)
                # os.remove(os.path.join(path, f))
                try:
                    os.mkdir(os.path.join(path, "processed"))
                except FileExistsError:
                    pass

                os.rename(os.path.join(path, f), os.path.join(
                    os.path.join(path, "processed"), f))
        break


def identify_amc():
    # logic is to identiy amc from excel sheet.
    # logiic is simple loop through amc's and find the maximum occurance of a single amc name in all sheets

    amc_names = []

    for amc in AMC.objects.all():
        name = amc.name
        name = name.replace("Mutual Fund", "").strip()
        name = name.replace("Mahindra", "").strip()  # for kotak mahindra
        name = name.replace("Financial", "").strip()  # for jm financial
        name = name.replace("Templeton", "").strip()  # for franklin
        name = name.replace("Aditya", "").strip()  # for absl

        # we can also try another logic i.e finding the common word among all fund names
        # instead of removing above manually. but will see that later on
        amc_names.append(name)

    amc_names.append("escorts")
    # quant mf aquired escrots so there older portfolio have name escorts

    print(amc_names)

    for (dirpath, dirnames, filenames) in os.walk(path):
        for f in filenames:
            if "lock" in f:
                continue

            if ".xls" in f.lower() or ".xlsx" in f.lower():

                try:
                    print("reading file ", os.path.join(path, f))
                    # xls = pd.ExcelFile(os.path.join(path, f))
                    xls = ExcelFile(os.path.join(path, f))
                    try:
                        sheet_names = xls["sheet_names"]
                    except:
                        sheet_names = xls.sheet_names

                    amc_sheet_match = {}

                    for sheet_name in sheet_names:
                        if sheet_name == "Index" or sheet_name == "Sheet1":
                            continue
                        # print("checking for sheet name", sheet_name)
                        # df1 = pd.read_excel(xls, sheet_name)
                        df1 = read_excel(xls, sheet_name)

                        mask = df1.apply(lambda x: x.astype(
                            str).str.contains('ISIN', False))
                        df2 = df1[mask.any(axis=1)]

                        # print(df2)

                        indexes = df2.index.values

                        if len(indexes) > 0:
                            df1 = df1.head(indexes[0])
                            # print(df1)
                            amc, score = match_fund_name_from_sheet(
                                amc_names, df1)

                            if score > 0:
                                if amc in amc_sheet_match:
                                    amc_sheet_match[amc] += 1
                                else:
                                    amc_sheet_match[amc] = 1
                        else:
                            print("isin not found!")
                            # pass

                    max_count = 0
                    max_amc = False

                    for amc in amc_sheet_match:
                        count = amc_sheet_match[amc]
                        if count > max_count:
                            max_count = count
                            max_amc = amc

                    print("amc identified as ", max_amc)

                    if max_amc != False:
                        if len(sheet_names) > 2:
                            # will read data from sheet 2
                            df1 = read_excel(xls, 2)
                        else:
                            df1 = read_excel(xls, 0)
                        date = find_date_from_sheet(df1, f)

                        if date is not False:

                            print(date, "date found")

                            m = date.strftime("%b")
                            y = date.strftime("%Y")

                            try:

                                if not os.path.exists(os.path.join(path, max_amc)):
                                    os.mkdir(os.path.join(path, max_amc))

                                if not os.path.exists(os.path.join(path, max_amc, y)):
                                    os.mkdir(os.path.join(path, max_amc, y))

                                if not os.path.exists(os.path.join(path, max_amc, y, m)):
                                    os.mkdir(os.path.join(path, max_amc, y, m))

                                print(os.path.join(path, f))
                                print(os.path.join(
                                    os.path.join(path, max_amc, y, m), f))

                                os.chmod(os.path.join(
                                    path, max_amc, y, m), 777)

                                # os.rename(os.path.join(path, f), os.path.join(
                                #     os.path.join(path, max_amc, y, m), f))

                                shutil.copy(os.path.join(path, f),
                                            os.path.join(path, max_amc, y, m))

                                os.remove(os.path.join(path, f))

                            except Exception as e:
                                traceback.print_exc(e)
                                print(e)
                        else:
                            print("date not found! see data")
                    else:
                        print("amc not found! see data")
                        break

                    # print(amc_sheet_match)
                except Exception as e:
                    traceback.print_exc(e)
                    print(e)

                # break

        break

    pass


def find_date_from_sheet(df, file_name=False):
    # trying to find date from sheet. logic mainly depends on "As on" which is mentioned in every sheet
    # so trying to identity which cell has "as on" mentioned and then find date in that cell
    mask = df.apply(lambda x: x.astype(
        str).str.contains('as on|month ended', False))
    df1 = df[mask.any(axis=1)]
    df1 = df1.fillna(0)
    # print(df1)

    cells = []

    for cell in df1.columns:
        if cell != 0:
            cells.append(cell)

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

        if "as on" in str(cell) or "for the month ended" in str(cell):
            # print(cell)
            try:
                cell = cell[cell.index("as on")+len("as on"):]
            except:
                cell = cell[cell.index(
                    "for the month ended")+len("for the month ended"):]

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


def match_fund_name_from_sheet(fund_names, sheet_df):
    df1 = sheet_df.fillna(0)
    df1 = df1.head()
    # print(df1.to_numpy())
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
