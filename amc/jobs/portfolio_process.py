import pandas as pd
import numpy as np
import requests
import datetime
import traceback
import shutil

import os

from amc.models import AMC_Portfolio_Process, Scheme_Portfolio, Scheme_Portfolio_Data

from todo.models import Scheme, AMC
from amc.jobs.util import generic_process_zip_file, ExcelFile, read_excel, match_fund_name_from_sheet, find_date_from_sheet, find_row_with_isin_heading, get_amc_common_names

from amc.jobs.util import portfolio_path as mf_download_files_path, local_base_path, server_base_path


"""
https://mutualfund.adityabirlacapital.com/forms-and-downloads/portfolio
https://www.barodamf.com/Downloads/Pages/Latest-Factsheet-and-Profile.aspx
https://dspim.com/about-us/mandatory-disclosure/portfolio-disclosures
https://www.hdfcfund.com/statutory-disclosure/monthly-portfolio
https://www.principalindia.com/all-downloads/disclosures
http://www.quant-mutual.com/statutory-disclosures
https://www.jmfinancialmf.com/Downloads/FactSheets.aspx?SubReportID=A49C5853-C27A-42C5-9703-699AFEACE164
https://assetmanagement.kotak.com/portfolios
https://www.licmf.com/statutory-disclosure
https://www.icicipruamc.com/Downloads/MonthlyPortfolioDisclosure.aspx
https://www.reliancemutual.com/investor-service/downloads/factsheets
https://www.sbimf.com/en-us/portfolios
https://www.tatamutualfund.com/downloads/monthly-portfolio
https://www.taurusmutualfund.com/Download/portfolio.php
https://www.franklintempletonindia.com/investor/reports
https://www.utimf.com/about/statutory-disclosures/scheme-dashboard
https://www.canararobeco.com/statutory-disclosures/scheme-monthly-portfolio
https://www.sundarammutual.com/Monthly_Portfolio
http://www.saharamutual.com/downloads/MonthlyPortfolio.aspx
https://www.boiaxamf.com/investor-corner#t2
https://www.edelweissmf.com/statutory#Monthly-Portfolio-of-Schemes
https://www.idfcmf.com/download-centre.aspx?tab=disclosures
https://www.axismf.com/statutory-disclosures
https://www.motilaloswalmf.com/downloads/mutual-fund/Month-End-Portfolio
https://www.ltfs.com/companies/lnt-investment-management/statutory-disclosures.html
https://www.idbimutual.co.in/Downloads/Fund-Portfolios
http://www.dhflpramericamf.com/statutory-disclosure/monthlyportfolio
https://www.bnpparibasmf.in/downloads/monthly-portfolio-scheme
http://www.unionmf.com/downloads/others/monthlyportfolios.aspx
https://www.iiflmf.com/downloads/disclosures
http://www.indiabullsamc.com/portfolio-disclosure/
https://shriramamc.com/StatDis-MonthlyPort.aspx
https://www.mahindramutualfund.com/downloads#MANDATORY-DISCLOSURES
https://www.miraeassetmf.co.in/downloads/portfolios
https://www.yesamc.in/regulatory-disclosures/monthly-and-half-yearly-portfolio-disclosures
http://amc.ppfas.com/downloads/portfolio-disclosure/
http://www.itimf.com/statutory-disclosure/monthly-portfolios

"""

# need to figure out multiple things in this
# 1. how to download different excel sheets from diffrent mf providers
# 2. need some kind of error report if portfolio import fails
# 3. there are multiple funds like bharatcon serial1, 2, 3 etc need to see how to fix this
# 4. need to be able to find out if for certain funds portfolio was not import or for full house


def process_zip_file():
    # many mf have portfolio as zip files so first we need to extract them

    generic_process_zip_file(mf_download_files_path)
    identify_amc()


def move_files_from_folder_to_parent():
    # this is temporary one time function i made to move all processed files from
    # amc directorys back to original path for testing purposes

    for (dirpath, dirnames, filenames) in os.walk(mf_download_files_path):
        for f in filenames:
            if "lock" in f:
                continue

            if ".xls" in f.lower() or ".xlsx" in f.lower():
                print(os.path.join(dirpath, f))
                os.rename(os.path.join(dirpath, f),
                          os.path.join(mf_download_files_path, f))

    pass


def identify_amc():
    # logic is to identiy amc from excel sheet.
    # logiic is simple loop through amc's and find the maximum occurance of a single amc name in all sheets

    amc_names = get_amc_common_names()
    print(amc_names)

    for (dirpath, dirnames, filenames) in os.walk(mf_download_files_path):
        for f in filenames:
            if "lock" in f:
                continue

            if ".xls" in f.lower() or ".xlsx" in f.lower():

                try:

                    amc_process = AMC_Portfolio_Process(
                        file_name=os.path.join(mf_download_files_path, f))
                    amc_process.save()

                    print("reading file ", os.path.join(
                        mf_download_files_path, f))

                    amc_process.addLog("reading file " +
                                       os.path.join(mf_download_files_path, f))

                    # xls = pd.ExcelFile(os.path.join(path, f))
                    xls = ExcelFile(os.path.join(mf_download_files_path, f))
                    try:
                        sheet_names = xls["sheet_names"]
                    except:
                        sheet_names = xls.sheet_names

                    amc_sheet_match = {}

                    for sheet_name in sheet_names:
                        if sheet_name == "Index" or sheet_name == "Sheet1":
                            continue
                        print("checking for sheet name", sheet_name)
                        # df1 = pd.read_excel(xls, sheet_name)
                        df1 = read_excel(xls, sheet_name)

                        mask = df1.apply(lambda x: x.astype(
                            str).str.contains('ISIN', False))
                        df2 = df1[mask.any(axis=1)]

                        # print(df2)

                        indexes = df2.index.values

                        if len(indexes) > 0:
                            # df1 = df1.head(indexes[0])
                            # print(df1)
                            amc, score = match_fund_name_from_sheet(
                                amc_names, df1)

                            print(amc , "xxxx", score)

                            if score > 0:
                                if amc in amc_sheet_match:
                                    amc_sheet_match[amc] += 1
                                else:
                                    amc_sheet_match[amc] = 1
                        else:
                            amc_process.addLog(
                                "isin not found! in sheet " + sheet_name)
                            # print(df1)
                            print("isin not found! in sheet " + sheet_name)
                            # pass

                    max_count = 0
                    max_amc = False

                    for amc in amc_sheet_match:
                        count = amc_sheet_match[amc]
                        if count > max_count:
                            max_count = count
                            max_amc = amc

                    amc_process.setAMC(max_amc)

                    amc_process.addLog("amc identified as " + str(max_amc))

                    if max_amc != False:
                        if len(sheet_names) > 2:
                            # will read data from sheet 2
                            df1 = read_excel(xls, 2)
                        else:
                            df1 = read_excel(xls, 0)
                        date = find_date_from_sheet(df1, f)

                        if date is not False:

                            amc_process.addLog(
                                "date found " + date.strftime('%m/%d/%Y'))

                            m = date.strftime("%b")
                            y = date.strftime("%Y")

                            try:

                                if not os.path.exists(os.path.join(mf_download_files_path, max_amc)):
                                    os.mkdir(os.path.join(
                                        mf_download_files_path, max_amc))

                                if not os.path.exists(os.path.join(mf_download_files_path, max_amc, y)):
                                    os.mkdir(os.path.join(
                                        mf_download_files_path, max_amc, y))

                                if not os.path.exists(os.path.join(mf_download_files_path, max_amc, y, m)):
                                    os.mkdir(os.path.join(
                                        mf_download_files_path, max_amc, y, m))

                                amc_process.addLog(os.path.join(
                                    mf_download_files_path, f))
                                amc_process.addLog(os.path.join(
                                    os.path.join(mf_download_files_path, max_amc, y, m), f))
                                print(os.path.join(mf_download_files_path, f))
                                print(os.path.join(
                                    os.path.join(mf_download_files_path, max_amc, y, m), f))

                                # os.chmod(os.path.join(
                                #     mf_download_files_path, max_amc, y, m), 777)

                                # os.rename(os.path.join(path, f), os.path.join(
                                #     os.path.join(path, max_amc, y, m), f))

                                os.rename(os.path.join(mf_download_files_path, f),
                                            os.path.join(mf_download_files_path, max_amc, y, m))

                                amc_process.setFinalFilePath(os.path.join(
                                    os.path.join(mf_download_files_path, max_amc, y, m), f))

                                process_data(amc_process)

                                # os.rename(os.path.join(
                                #     mf_download_files_path, f), os.path.join(
                                #     mf_download_files_path, "processed", f))

                            except Exception as e:
                                traceback.print_exc(e)
                                amc_process.addCritical(e)
                                print(e)
                        else:
                            amc_process.addCritical("date not found! see data")
                            print("date not found! see data")
                    else:
                        amc_process.addCritical("amc not found! see data")
                        print("amc not found! see data")
                        break

                    # print(amc_sheet_match)
                except Exception as e:
                    traceback.print_exc(e)
                    amc_process.addCritical(e)
                    print(e)

                # break

        break

    pass


def process_data(amc_process):

    # to_process = AMC_Portfolio_Process.objects.get_portfolio_to_process(5)
    # for amc_process in to_process:
    file_path = getattr(amc_process, "final_path")
    amc_short_name = getattr(amc_process, "amc")

    print(file_path, "xxxxxxxxxxxxxxxxxxxxxxxx")

    # one time temporary code since we parsed files in local it has local path
    if local_base_path in file_path:
        file_path = file_path.replace(local_base_path, server_base_path)

    amc = AMC.objects.match_amc_with_short_name(amc_short_name)

    if amc != False:
        try:
            process_portfolio(file_path, amc, getattr(
                amc_process, "date"), amc_process)
            amc_process.parsing_completed()
        except Exception as e:
            print(e)
            amc_process.addCritical(e)
            amc_process.parsing_completed()
            traceback.print_exc(e)

        # break

    else:
        print("unable to match amc")
        amc_process.addCritical("Unable to match amc itself!")
        amc_process.parsing_completed()


def process_portfolio(filename, amc, date, amc_process):

    print("filename ", filename)
    print("amc ", amc.name)

    xls = ExcelFile(filename)

    schemes = Scheme.objects.filter(amc=amc)

    fund_names = {}

    for scheme in schemes:
        fund_name = scheme.get_clean_name()
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

        fund, ratio = match_fund_name_from_sheet    (fund_names.keys(), df1)

        print(fund, "===",  ratio, "===", sheet_name)

        if fund is not None:
            col_indexes = find_row_with_isin_heading(df1, fund_names[fund])

            scheme = fund_names[fund]

            try:
                scheme_port = Scheme_Portfolio_Data.objects.get(
                    scheme=scheme, date=date)
                Scheme_Portfolio.objects.filter(scheme=scheme_port).delete()
                scheme_port.delete()
            except Exception as e:
                print(e)

            scheme_data = Scheme_Portfolio_Data(
                scheme=scheme,
                url=filename,
                date=date
            )
            scheme_data.save()

            print(scheme_data)

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

                print(df1.iloc[col_indexes["row_index"]:, col_indexes["indexes"]])

                df2 = df1.iloc[(col_indexes["row_index"]+1):, col_indexes["indexes"]]
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
                                scheme=scheme_data,
                                name=name,
                                isin=isin,
                                quantity=quantity,
                                coupon=coupon,
                                rating=rating,
                                market=market,
                                percent=nav_per
                            )
                            scheme_portfolio.save()

                        else:
                            # this is stock
                            scheme_portfolio = Scheme_Portfolio(
                                scheme=scheme_data,
                                name=name,
                                isin=isin,
                                quantity=quantity,
                                industry=rating,
                                market=market,
                                percent=nav_per
                            )
                            try:
                                scheme_portfolio.save()
                            except Exception as e:
                                print(e)
                                print(scheme_data)
                                print(isin)
                                # traceback.print_exc(e)
                                pass
                            

                    else:
                        if quantity != False and rating != False:
                            # looks like unlisted stock or bond
                            if coupon != False:
                                scheme_portfolio = Scheme_Portfolio(
                                    scheme=scheme_data,
                                    name=name,
                                    quantity=quantity,
                                    coupon=coupon,
                                    rating=rating,
                                    market=market,
                                    percent=nav_per
                                )
                                scheme_portfolio.save()
                            else:
                                scheme_portfolio = Scheme_Portfolio(
                                    scheme=scheme_data,
                                    name=name,
                                    quantity=quantity,
                                    industry=rating,
                                    market=market,
                                    percent=nav_per
                                )
                                scheme_portfolio.save()
                        else:
                            # this is general classification. not saving this for now
                            pass

                    # print(name)

                Scheme_Portfolio_Data.objects.filter(
                    id=scheme_data.id).update(parsed=False)
                print("columns present")
                #
            else:
                print("unable to read data key columns missing")
                # raise Exception("unable to read data key columns missing")
        else:
            print("fund itself not found")
            # amc_process.addLog("fund not found ", )
            # raise Exception("found itself not found")
