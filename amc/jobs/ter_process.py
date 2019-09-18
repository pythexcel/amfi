import pandas as pd
import numpy as np
import requests
import datetime
import traceback
import zipfile
import os
import shutil
import json
import datefinder
from colorama import Fore, Back, Style, init

from bs4 import BeautifulSoup


from amc.models import AMC_Portfolio_Process, Scheme_Portfolio, Scheme_Portfolio_Data

from todo.models import Scheme, AMC
from amc.jobs.util import generic_process_zip_file, ExcelFile, read_excel, match_fund_name_from_sheet, find_date_from_sheet, find_row_with_isin_heading, get_amc_common_names

from amc.jobs.util import ter_path

from fuzzywuzzy import fuzz, process

from amc.models import Scheme_TER_Process, Scheme_TER_Process_Log, Scheme_TER
from subprocess import call


# //https://www.amfiindia.com/ter-of-mf-schemes  explore this . this can highly simplify the code for TER

def start_process():

    cats = Scheme.get_fund_categorization()

    for key in cats:
        for row in cats[key]:
            print(row['Text'], "xxx", row['Value'])
            today = datetime.date.today()
            download_data(row["Value"], today.month, today.year)


def download_data(cat_desc, month, year):

    response = requests.post("https://www.amfiindia.com/modules/LoadTERData", data={
        "MonthTER": str(month) + "-" + str(year),
        "MF_ID": "-1",
        "NAV_ID": "1",
        "SchemeCat_Desc": cat_desc
    })

    soup = BeautifulSoup(response.text, 'html.parser')

    data = soup.find("table")

    ter_data = []

    for row in data.findAll('tr'):
        col = row.findAll('td')
        if len(col) > 1:
            # there is an issue here, the current data which we get back
            # has data for multiple date of same month. which is not needed.
            # we just need to one data point for a month which is the latest
            scheme_name = col[0].string
            date = col[1].string
            ter = col[-1].string
            date = datetime.datetime.strptime(date, "%d-%b-%Y")
            # print(scheme_name, "xxx", date, "xxx", ter)

            ter_data.append([scheme_name, date, ter])

    df = pd.DataFrame(ter_data, columns=['Scheme', 'Date', "Ter"])

    df = df.drop_duplicates(
        subset="Scheme", keep="last")

    print(df)

    for row in df.itertuples():
        scheme_name = row.Scheme
        date = row.Date
        ter = row.Ter

        scheme = Scheme.objects.filter(fund_name=scheme_name).first()
        if scheme:
            print("scheme found ", scheme_name)
            ters = Scheme_TER.objects.filter(
                scheme=scheme,
                date__year=date.year, date__month=date.month)
            ters.delete()

            tr_db = Scheme_TER(
                scheme=scheme,
                date=date,
                ter=ter
            )
            tr_db.save()

        else:
            print(Fore.RED + "scheme not found with name ", scheme_name)
            # break

    # switch to amfi website as it has all amc's in a single location
    # below code is all old not used any more.
    # no point in parsing xml files when amfi has data already
    return
    # process_zip_file()
    # process_file()

    # move_files_from_folder_to_parent()

    # Scheme_TER_Process
    pass


"""
https://mutualfund.adityabirlacapital.com/forms-and-downloads/total-expense-ratio
https://www.barodamf.com/Downloads/Pages/expenseratio.aspx
https://www.dspim.com/quick-links/total-expense-ratio-of-mutual-fund-schemes
https://www.hdfcfund.com/statutory-disclosure/total-expense-ratio-of-mutual-fund-schemes/reports
https://www.principalindia.com/all-downloads/disclosures
http://www.quant-mutual.com/statutory-disclosures
https://www.jmfinancialmf.com/Downloads/Remuneration.aspx?SubReportID=0383C306-CFB7-4CFE-B516-2A8FE89ABF5D
https://assetmanagement.kotak.com/total-expense-ratio
https://www.licmf.com/total-expense-ratio
https://www.icicipruamc.com/Downloads/total-expense-ratio.aspx
https://www.reliancemutual.com/investor-services/downloads/total-expense-ratio-of-mutual-fund-schemes
https://www.sbimf.com/en-us/disclosure/total-expense-ratio-of-mutual-fund-schemes
https://www.taurusmutualfund.com/scheme_searchresult.php?to_date=18-07-2019&from_date=01-01-2019&schemecode=All
https://www.franklintempletonindia.com/investor/reports
https://www.utimf.com/forms-and-downloads/#js-ter-wrapper
https://www.canararobeco.com/investor-corner/total-expense-ratio
https://old.canararobeco.com/forms-downloads/Pages/expenseratio.aspx
https://www.sundarammutual.com/TER
http://www.saharamutual.com/downloads/TotalExpenseRatio.aspx
https://www.quantumamc.com/total-expense-ratio/report-1
https://www.boiaxamf.com/investor-corner#t4
https://www.edelweissmf.com/statutory
https://www.idfcmf.com/total-expense-ratio.aspx
https://www.axismf.com/total-expense-ratio
https://www.motilaloswalmf.com/downloads/mutual-fund/totalexpenseratio
https://www.ltfs.com/companies/lnt-investment-management/statutory-disclosures.html
https://www.idbimutual.co.in/statutory-disclosure/total-expense-ratio-of-mutual-fund-schemes
http://www.dhflpramericamf.com/statutory-disclosure/portfolio-related/expense-ratio
https://www.bnpparibasmf.in/downloads/total-expense-ratio-of-mutual-fund-schemes
http://www.unionmf.com/downloads/TotalExpenseRatioOfMutualFundSchemes.aspx
https://www.iiflmf.com/expenses-ratio
http://www.indiabullsamc.com/downloads/total-expense-ratio-of-mutual-fund-schemes/
https://www.shriramamc.com/TER-Latest.aspx
https://www.mahindramutualfund.com/downloads#MANDATORY-DISCLOSURES
https://www.miraeassetmf.co.in/downloads/total-expense-ratio
https://invescomutualfund.com/about-us?tab=Statutory&active=ExpenseRatioDisclosure
https://www.yesamc.in/regulatory-disclosures/total-expense-ratio-of-mutual-funds-schemes
http://amc.ppfas.com/statutory-disclosures/total-expense-ratio-TER/
http://www.itimf.com/statutory-disclosure/total-expense-ratio
https://www.invescomutualfund.com/about-us?tab=Statutory&active=ExpenseRatioDisclosure
"""
# entire code and effort below is waste!!!!
# it works well but amfi just created a page for TER !!!
# aaahhhhhhhhhhhhhh... koi nai. its better.
# below code can be used if needed

# def move_files_from_folder_to_parent():
#     # this is temporary one time function i made to move all processed files from
#     # amc directorys back to original path for testing purposes

#     from amc.jobs.util import server_base_path

#     print(os.path.join(server_base_path, "amfi", "data", "ter"))

#     for (dirpath, dirnames, filenames) in os.walk(os.path.join(server_base_path, "amfi", "data", "ter")):
#         for f in filenames:
#             if "lock" in f:
#                 continue

#             # if ".xls" in f.lower() or ".xlsx" in f.lower():
#             print(os.path.join(dirpath, f))
#             shutil.copy(os.path.join(dirpath, f),
#                         os.path.join(ter_path, f))

#     pass


# def process_file():
#     for (dirpath, dirnames, filenames) in os.walk(ter_path):
#         for f in filenames:
#             if "lock" in f:
#                 continue

#             if ".xls" in f.lower() or ".xlsx" in f.lower():

#                 # process_ter(os.path.join(ter_path, f), f)
#                 # break

#                 try:
#                     os.mkdir(os.path.join(ter_path, "processed_files"))
#                 except FileExistsError:
#                     pass

#                 shutil.copy(os.path.join(ter_path, f), os.path.join(
#                     ter_path, "processed_files", f))

#                 process_ter(os.path.join(
#                     os.path.join(ter_path, "processed_files"), f), f)

#                 # break

#         break  # this break is important to prevent further processing of sub directories
#     pass


# def process_zip_file():
#     # many mf have portfolio as zip files so first we need to extract them
#     generic_process_zip_file(ter_path)


# def process_ter(filename, f):

#     print("filename ", filename)
#     # print("amc ", amc.name)

#     #  = "/mnt/c/work/newdref/mf_ter_download/Total Expense Ratio of Mutual Fund Schemes.xlsx"

#     ter_process = Scheme_TER_Process(file_name=filename)
#     ter_process.save()

#     xls = ExcelFile(filename)

#     try:
#         sheet_names = xls["sheet_names"]
#     except:
#         sheet_names = xls.sheet_names

#     if len(sheet_names) > 5:
#         print(" multiple sheets means ter is divided into different sheets. hence our default approach wont work ")
#         ter_process.addLog(
#             "multiple sheets means ter is divided into different sheets. hence our default approach wont work")

#         df1 = read_excel(xls, 0)

#         df_copy = df1.copy()

#         print(df_copy)

#         indexes = find_col_index(df1, "Scheme")

#         amc = None
#         if len(indexes) > 0:
#             col_indexes = {}
#             col_indexes["Scheme"] = indexes[0]

#             columns = [""] * df1.shape[1]

#             df1.columns = columns

#             for key in col_indexes:
#                 if key != "row_index" and key != "indexes":
#                     idx = col_indexes[key]
#                     columns[idx] = key

#             # print(columns)

#             df1.columns = columns

#             schemes = df1.loc[:, "Scheme"].values

#             amc, final_amc = identify_amc_from_scheme_array(schemes)

#             print("final amc ", final_amc, " amc ", amc)

#         if amc is None:
#             print(
#                 "this means amc not found means there is no index column so lets try with scheme name")

#             df1 = read_excel(xls, 2)
#             df1.loc[-1] = df1.columns
#             df1.index = df1.index + 1
#             df1 = df1.sort_index()
#             row_index = find_row_index(df1, "Name of Scheme")
#             print(df1)
#             print(row_index)

#             if row_index != -1:
#                 df1 = df1.fillna(False)
#                 scheme_name_row = df1.iloc[row_index].values

#                 print("scheme name row")
#                 print(scheme_name_row)

#                 amc, final_amc = identify_amc_from_scheme_name(scheme_name_row)

#         if amc is not None:

#             print("amc found", final_amc)

#             ter_process.setAMC(getattr(amc, "name"))

#             schemes = Scheme.objects.filter(amc=amc)

#             scheme_sheet_map = {}

#             scheme_names = []
#             scheme_name_map = {}

#             for scheme in schemes:
#                 name = getattr(scheme, "fund_name")
#                 print(name)
#                 scheme_names.append(name)
#                 scheme_name_map[name] = scheme

#             for sheet in sheet_names:
#                 if sheet == sheet_names[0]:
#                     continue

#                 df1 = read_excel(xls, sheet)
#                 # print(df1)

#                 row_index = find_row_index(df1, "Name of Scheme")

#                 if row_index != -1:
#                     df1 = df1.fillna(False)
#                     scheme_name_row = df1.iloc[row_index].values

#                     print("scheme name row")
#                     print(scheme_name_row)

#                     scheme_name = None
#                     for cell in scheme_name_row:
#                         if cell is False:
#                             continue

#                         if scheme_name is not None:
#                             continue

#                         for name in scheme_names:

#                             # print(name, "============", cell)
#                             if name == cell:
#                                 scheme_name = name
#                                 print("found scheme name", name,
#                                       " with direct match ", cell)

#                                 break

#                     for cell in scheme_name_row:
#                         if cell is False:
#                             continue

#                         if scheme_name is not None:
#                             continue

#                         for name in scheme_names:
#                             # print(name, "xxx", cell)
#                             # print(fuzz.token_set_ratio(name, cell))

#                             if fuzz.token_set_ratio(name, cell) > 95:
#                                 scheme_name = name
#                                 print("found scheme name", name,
#                                       " with fuzzy match ", cell)

#                                 break

#                     if scheme_name is not None:
#                         scheme_names.remove(scheme_name)
#                         scheme_sheet_map[sheet] = scheme_name

#                 else:
#                     print("name of scheme not found in sheet", sheet)

#             print("scheme mapped ", scheme_sheet_map)
#             print("scheme not found ", scheme_names)

#             ter_process.addLog(json.dumps(scheme_sheet_map))
#             ter_process.addLog(json.dumps(scheme_names))

#             for sheet in scheme_sheet_map:
#                 fund_name = scheme_sheet_map[sheet]
#                 df1 = read_excel(xls, sheet)
#                 col_indexes = find_head_row(df1.head(10))

#                 if "Date" in col_indexes and "Total_TER" in col_indexes:

#                     columns = [""] * df1.shape[1]

#                     df1.columns = columns

#                     for key in col_indexes:
#                         if key != "row_index" and key != "indexes":
#                             idx = col_indexes[key]
#                             columns[idx] = key

#                     df1.columns = columns

#                     df2 = df1.drop("", axis=1)
#                     df2 = df2.fillna(False)

#                     df2 = df2[df2["Total_TER"] != False]

#                     df2 = df2.drop_duplicates(
#                         subset="Total_TER", keep="last")
#                     # print(df2)
#                     print(fund_name)
#                     for row in df2.itertuples():
#                         print(row)
#                         save_row_to_db(row, scheme_name_map[fund_name])

#                 else:
#                     print("column not found")

#             move_file_finally(ter_path, amc, filename, f, ter_process)

#         else:
#             print("unable to identify amc")
#             ter_process.addCritical("columns not present unable to parse")

#         # else:
#         #     print("scheme column not found unable to process any further")
#         #     ter_process.addCritical("columns not present unable to parse")

#         return

#     df1 = pd.read_excel(xls, 0)

#     # print(df1.head(1))

#     col_indexes = find_head_row(df1.head(10))

#     # LIC MF has rows for regular/direct instead of column which is unique. so unique solution for it

#     if "Plan" in df1.columns:
#         df1 = df1[df1.Plan == "Direct Plan"]

#     print(col_indexes)

#     if "Scheme" in col_indexes and "Date" in col_indexes and "Total_TER" in col_indexes:

#         columns = [""] * df1.shape[1]

#         df1.columns = columns

#         for key in col_indexes:
#             if key != "row_index" and key != "indexes":
#                 idx = col_indexes[key]
#                 columns[idx] = key

#         # print(columns)

#         df1.columns = columns

#         # print(df1.iloc[col_indexes["row_index"]:, col_indexes["indexes"]])

#         # df2 = df1.iloc[(col_indexes["row_index"]+1):, col_indexes["indexes"]]

#         df2 = df1.drop("", axis=1)
#         df2 = df2.fillna(False)

#         df2 = df2[df2["Total_TER"] != False]

#         amc, amc_unique = identify_amc(df2)

#         if amc is not None:
#             print("found amc")
#             print(amc)
#             print(getattr(amc, "name"))

#             ter_process.setAMC(getattr(amc, "name"))

#             schemes = Scheme.objects.get_funds(amc=amc)

#             # df2 = df2.set_index("Scheme")
#             # print(df2)
#             print(df2.shape)

#             # df2 = df2[mask]
#             df4 = df2.drop_duplicates(subset="Scheme", keep="last")
#             print(df4.shape)

#             scheme_map = {}

#             scheme_name_map = {}
#             scheme_not_found = []
#             for fund in schemes:
#                 fund_name = fund.get_clean_name()
#                 scheme_name_map[fund_name] = fund
#                 mask = df4.apply(lambda x: fund_name ==
#                                  x["Scheme"], axis=1)

#                 df3 = df4[mask]

#                 if len(df3.index) > 0:
#                     # print(df3)
#                     df4.drop(labels=df3.index[0], axis=0, inplace=True)
#                     print("fund name direct match ", fund_name)
#                     # df3 = df3.drop_duplicates(subset="Total TER", keep="last")
#                     # print(df3)
#                     scheme_map[fund_name] = df3["Scheme"].iloc[0]
#                 else:
#                     # print("fund name not found or some other error", fund_name)
#                     scheme_not_found.append(fund_name)

#             # print(df4)

#             scheme_still_not_found = []
#             for fund_name in scheme_not_found:
#                 short_fund_name = fund_name.replace(amc_unique, "")

#                 def m(x):
#                     scheme = str(x["Scheme"]).lower().replace(
#                         amc_unique.lower(), "")
#                     # print(short_fund_name, "=====", scheme, "=====", fuzz.token_set_ratio(
#                     #     short_fund_name, scheme))
#                     return fuzz.token_set_ratio(
#                         short_fund_name, scheme) > 90 or fuzz.ratio(
#                         short_fund_name, scheme) >= 90

#                 mask = df4.apply(m, axis=1)
#                 df3 = df4[mask]

#                 if len(df3.index) > 0:
#                     # there is a problem in here in rare cases there can be multiple matches
#                     # i.e multiple places with ratio > 95
#                     # but we are always considering the index = 0 which is not correct in most cases
#                     # rather we should take the index with heighest score.
#                     # but its more cmplex logic so leaving it for now
#                     # fixing above now :) :)

#                     if len(df3.index) > 1:
#                         df3['ratio'] = df3.apply(lambda row: fuzz.token_set_ratio(
#                             fund_name, row["Scheme"]), axis=1)
#                         df3 = df3.sort_values(by="ratio")
#                         print(df3)

#                     df4.drop(labels=df3.index[0], axis=0, inplace=True)
#                     print("fund name fuzzy match ", fund_name,
#                           " with ", df3["Scheme"].iloc[0])
#                     scheme_map[fund_name] = df3["Scheme"].iloc[0]
#                 else:
#                     # print("fund name not found or some other error", fund_name)
#                     scheme_still_not_found.append(fund_name)

#             for fund_name in scheme_map:
#                 fund_map_name = scheme_map[fund_name]
#                 mask = df2.apply(lambda x: fund_map_name ==
#                                  x["Scheme"], axis=1)

#                 df3 = df2[mask]
#                 df3 = df3.drop_duplicates(subset="Total_TER", keep="last")
#                 print(fund_name)
#                 for row in df3.itertuples():
#                     print(row)

#                     save_row_to_db(row, scheme_name_map[fund_name])

#                 # print(df3)
#                 # break
#                 # df4.drop(labels=df3.index, axis=0)

#             """
#             # this is taking too long when data is too much i.e excel sheet has like 1500 rows
#             # the fuzzy match takes too long so need to optmize so comparing length
#             # need to reduce data
#             for fund_name in scheme_not_found:

#                 fund_name = fund_name.replace(amc_unique, "")

#                 def m(x):
#                     scheme = x["Scheme"].replace(amc_unique, "")
#                     print(scheme, 'xxx')

#                     return fuzz.token_set_ratio(
#                         fund_name, scheme) > 95

#                 mask = df4.apply(m, axis=1)
#                 df3 = df4[mask]

#                 if len(df3.index) > 0:
#                     # df2.drop(labels=df3.index, axis=0, inplace=True)
#                     print("fund name", fund_name)
#                     # df3 = df3.drop_duplicates(subset="Total TER", keep="last")
#                     # print(df3)
#                 else:
#                     # print("fund name not found or some other error", fund_name)
#                     scheme_not_found.append(fund_name)

#             """

#             move_file_finally(ter_path, amc, filename, f, ter_process)

#             # break
#             # print(scheme_map)
#             print(scheme_still_not_found)
#             ter_process.addLog(json.dumps(scheme_map))
#             ter_process.addLog(json.dumps(scheme_still_not_found))
#             # for row in df2.itertuples():
#             #     print(row)

#         else:
#             print("unable to identify amc!")
#             ter_process.addCritical("unable to identify amc!")
#     else:
#         ter_process.addCritical("columns not present unable to parse")
#         print(col_indexes)
#         print("columns not present unable to parse ", filename)


# def identify_amc(df):

#     df3 = df.drop_duplicates(subset="Scheme", keep="last")

#     df3 = df3.head(15)

#     schemes = df3.loc[:, "Scheme"].values

#     return identify_amc_from_scheme_array(schemes)


# def move_file_finally(ter_path, amc, filename, f, ter_process):
#     try:
#         os.mkdir(os.path.join(os.path.join(
#             ter_path, "processed_files"), getattr(amc, "name")))
#     except FileExistsError:
#         pass

#     os.rename(filename, os.path.join(os.path.join(os.path.join(
#         ter_path, "processed_files"), getattr(amc, "name")), f))

#     ter_process.updateFile(os.path.join(os.path.join(os.path.join(
#         ter_path, "processed_files"), getattr(amc, "name")), f))


# def identify_amc_from_scheme_name(scheme_names):
#     amcs = get_amc_common_names()
#     amc_score = {}

#     for amc_name in amcs:
#         for scheme_name in scheme_names:
#             if scheme_name is False:
#                 continue

#             if scheme_name is None:
#                 continue
#             print(amc_name, "xxx", scheme_name)
#             ratio = fuzz.token_set_ratio(amc_name, scheme_name)

#             if ratio > 95:
#                 if amc_name in amc_score:
#                     amc_score[amc_name] += 1
#                 else:
#                     amc_score[amc_name] = 1
#                 break

#     max_score = 0
#     final_amc = None

#     for key in amc_score:
#         if amc_score[key] > max_score:
#             final_amc = key

#     if final_amc is not None:
#         return AMC.objects.match_amc_with_short_name(final_amc), final_amc
#     else:
#         return None, None


# def identify_amc_from_scheme_array(schemes):
#     amcs = get_amc_common_names()
#     amc_score = {}

#     for amc_name in amcs:
#         for scheme_name in schemes:
#             if amc_name == "ITI" and "ITI " in str(scheme_name):
#                 print(amc_name, "xxx", scheme_name, " should be ITI")
#                 if amc_name in amc_score:
#                     amc_score[amc_name] += 1
#                 else:
#                     amc_score[amc_name] = 1
#                 continue

#             ratio = fuzz.token_set_ratio(amc_name, scheme_name)

#             if ratio > 95:
#                 print(amc_name, "xxx", scheme_name, " ratio ", ratio)
#                 if amc_name == "Mahindra":
#                     if "Kotak" in scheme_name:
#                         ratio = 0
#                         print("skpiping this match due to kotak mahindra issue")
#                         continue

#                 if amc_name in amc_score:
#                     amc_score[amc_name] += 1
#                 else:
#                     amc_score[amc_name] = 1
#                 break

#     max_score = 0
#     final_amc = None

#     print(amc_score)

#     for key in amc_score:
#         if amc_score[key] > max_score:
#             final_amc = key

#     if final_amc is not None:
#         return AMC.objects.match_amc_with_short_name(final_amc), final_amc
#     else:
#         return None, None


# def find_head_row(df):
#     # most of our logic is based on scheme in row
#         # this row is most important is present in all excel sheet

#     df.loc[-1] = df.columns
#     df.index = df.index + 1
#     df = df.sort_index()

#     # print(df)

#     col_indexes = {}

#     indexes = find_col_index(df, "Scheme")

#     # i have seen that all these expected cols can be in different rows so thats why this method

#     if len(indexes) > 0:
#         print(indexes)
#         col_indexes["Scheme"] = indexes[0]
#         if len(indexes) > 1:
#             # this means multiple scheme columns. but we need exact scheme name only
#             print(
#                 "this means multiple scheme columns. but we need exact scheme name only")
#             indexes2 = find_col_index(df, "Name")
#             print(indexes2)
#             intersect = list(set(indexes).intersection(indexes2))
#             if len(intersect) > 0:
#                 col_indexes["Scheme"] = intersect[0]

#     indexes = find_col_index(df, "Date")

#     if len(indexes) > 0:
#         col_indexes["Date"] = indexes[0]

#     if ("Scheme" in col_indexes and "Date" in col_indexes) and col_indexes["Scheme"] == col_indexes["Date"]:
#         # some issue!! both cannot be same index
#         # if they are same it means that the are in different rows and the word scheme is there two times
#         print("both index sames for date, scheme try to solve it ")
#         indexes = find_col_index(df, "Scheme", True)

#         if len(indexes) > 0:
#             col_indexes["Scheme"] = indexes[0]

#     indexes = find_col_index(df, "Total TER")

#     if len(indexes) > 0:
#         # Total TER is special columun and it will repeat muliptle times
#         # mainly because of direct/regular/etc plans
#         # 99% cases the 1st is regular, 2nd is direct
#         # code below is based on that assumption
#         if len(indexes) == 1:
#             col_indexes["Total_TER"] = indexes[0]
#         else:
#             col_indexes["Total_TER"] = indexes[1]

#     # if len(indexes) > 0:
#     #     index = indexes[0]
#     #     base_row_index = index

#     #     col_indexes["row_index"] = base_row_index

#     #     base_row = df.iloc[index].to_numpy()

#     #     # Total TER is special columun and it will repeat muliptle times
#     #     # mainly because of direct/regular/etc plans
#     #     # 99% cases the 1st is regular, 2nd is direct
#     #     # code below is based on that assumption

#     #     ter_occurance = 0
#     #     print(base_row)
#     #     indexes = []
#     #     for col in expected_cols:
#     #         i = 0
#     #         for val in base_row:
#     #             val = str(val)
#     #             ratio = fuzz.token_set_ratio(col, val)
#     #             # print(ratio, "==", col, val)
#     #             if col in val or ratio > 95:
#     #                 # i = list(base_row).index(val)
#     #                 indexes.append(i)

#     #                 if col == "Total TER" and ter_occurance > 1:
#     #                     continue

#     #                 col_indexes[col] = i
#     #                 if col == "Total TER":
#     #                     ter_occurance += 1
#     #                 if col != "Total TER":
#     #                     break
#     #             i += 1

#     #     col_indexes["indexes"] = indexes

#     # print(col_indexes)
#     return col_indexes


# def find_row_index(df, to_match):

#     mask = df.apply(lambda x: x.astype(str).str.contains(to_match, False))
#     df1 = df[mask.any(axis=1)]

#     # print(df1)

#     indexes = df1.index.values

#     if len(indexes) > 0:
#         return indexes[0]
#     else:
#         return -1


# def find_col_index(df, col_name, strict=False):
#     # df = df.fillna(False)
#     mask = df.apply(lambda x: x.astype(str).str.contains(col_name, False))
#     df1 = df[mask.any(axis=1)]

#     # print(col_name)
#     # print(df1)

#     indexes = df1.index.values

#     # print(indexes)

#     if len(indexes) > 0:
#         if strict is False:
#             index = indexes[0]

#             if col_name == "Name":
#                 index = indexes[1]
#                 # this is a hard coded fixes because many times we have "unnamed: 0 " columns in our database
#                 # basically when column is empty its replaced with unnamed

#             base_row = df.iloc[index].to_numpy()

#             # print(base_row)
#             indexes = []
#             for val in base_row:
#                 val = str(val)
#                 ratio = fuzz.token_set_ratio(col_name, val)
#                 # print(col_name, "xxx", val, " ratio ", ratio)
#                 if col_name in val or ratio > 95:
#                     i = list(base_row).index(val)
#                     indexes.append(i)

#         else:
#             for index in indexes:
#                 base_row = df.iloc[index].to_numpy()
#                 indexes = []
#                 for val in base_row:
#                     val = str(val)
#                     if col_name == val:
#                         i = list(base_row).index(val)
#                         indexes.append(i)

#     return indexes


# def save_row_to_db(row, scheme):
#     date = None
#     if row.Date is False:
#         return
#     if isinstance(row.Date, pd._libs.tslibs.timestamps.Timestamp):
#         date = row.Date.to_pydatetime()
#     else:
#         if isinstance(row.Date, datetime.date):
#             date = row.Date
#         else:
#             matches = datefinder.find_dates(row.Date)
#             for date in matches:
#                 break

#     if date is not None:
#         ter = row.Total_TER
#         print(date)
#         if isinstance(ter, str):
#             ter = ter.replace("%", '')
#             ter = float(ter)

#         try:
#             sc = Scheme_TER.objects.get(
#                 scheme=scheme, date=date)
#             Scheme_TER.objects.filter(pk=sc.id).update(ter=ter)
#         except:
#             tr_db = Scheme_TER(
#                 scheme=scheme,
#                 date=date,
#                 ter=ter
#             )
#             tr_db.save()

#     else:
#         print("unable to identify date!!")
