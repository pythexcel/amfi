import pandas as pd
import numpy as np
import requests
import datetime
import traceback

import os

from amc.models import AMC_Portfolio_Process, Scheme_Portfolio, Scheme_Portfolio_Data

from todo.models import Scheme, AMC
from amc.jobs.util import ExcelFile, read_excel, match_fund_name_from_sheet, find_date_from_sheet, find_row_with_isin_heading, get_amc_common_names

from amc.jobs.util import path as mf_download_files_path


def process_data():

    to_process = AMC_Portfolio_Process.objects.get_portfolio_to_process(5)
    for amc_process in to_process:
        file_path = getattr(amc_process, "final_path")
        amc_short_name = getattr(amc_process, "amc")

        amc = AMC.objects.match_amc_with_short_name(amc_short_name)

        if amc != False:
            try:
                process_portfolio(file_path, amc, getattr(amc_process, "date"))
                amc_process.parsing_completed()
            except Exception as e:
                amc_process.addCritical(e)
                # traceback.print_exc(e)

            # break

        else:
            amc_process.addCritical("Unable to match amc itself!")
            amc_process.parsing_completed()


def process_portfolio(filename, amc, date):

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

        fund, ratio = match_fund_name_from_sheet(fund_names.keys(), df1)

        print(fund, "===",  ratio, "===", sheet_name)

        if fund is not None:
            col_indexes = find_row_with_isin_heading(df1, fund_names[fund])

            scheme = fund_names[fund]

            Scheme_Portfolio_Data.objects.filter(scheme=scheme,
                                                 date=date).delete()

            scheme_data = Scheme_Portfolio_Data(
                scheme=scheme,
                url=filename,
                date=date
            )
            scheme_data.save()

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

                print(df1.iloc[col_indexes["row_index"]                               :, col_indexes["indexes"]])

                df2 = df1.iloc[(col_indexes["row_index"]+1)                               :, col_indexes["indexes"]]
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
                            scheme_portfolio.save()

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
                raise Exception("unable to read data key columns missing")
        else:
            print("fund itself not found")
            raise Exception("found itself not found")
