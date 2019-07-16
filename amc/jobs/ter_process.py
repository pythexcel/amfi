import pandas as pd
import numpy as np
import requests
import datetime
import traceback

import os

from amc.models import AMC_Portfolio_Process, Scheme_Portfolio, Scheme_Portfolio_Data

from todo.models import Scheme, AMC
from amc.jobs.util import ExcelFile, read_excel, match_fund_name_from_sheet, find_date_from_sheet, find_row_with_isin_heading, get_amc_common_names

from amc.jobs.util import path as mf_download_files_path, local_path, server_path

from fuzzywuzzy import fuzz, process


def process_ter():

    # print("filename ", filename)
    # print("amc ", amc.name)

    filename = "/mnt/c/work/newdref/mf_ter_download/Total Expense Ratio of Mutual Fund Schemes.xlsx"

    xls = ExcelFile(filename)

    df1 = pd.read_excel(xls, 0)

    columns = [""] * df1.shape[1]

    df1.columns = columns

    col_indexes = find_head_row(df1.head())

    if "Scheme" in col_indexes and "Date" in col_indexes and "Total TER" in col_indexes:

        for key in col_indexes:
            if key != "row_index" and key != "indexes":
                idx = col_indexes[key]
                columns[idx] = key

        # print(columns)

        df1.columns = columns

        # print(df1.iloc[col_indexes["row_index"]:, col_indexes["indexes"]])

        # df2 = df1.iloc[(col_indexes["row_index"]+1):, col_indexes["indexes"]]

        df2 = df1.drop("", axis=1)
        df2 = df2.fillna(False)

        df2 = df2[df2["Total TER"] != False]

        amc, amc_unique = identify_amc(df2)

        if amc is not None:
            print("found amc")
            print(amc)
            print(getattr(amc, "name"))

            schemes = Scheme.objects.get_funds(amc=amc)

            # df2 = df2.set_index("Scheme")
            # print(df2)

            print(df2.shape)
            scheme_not_found = []
            for fund in schemes:
                fund_name = getattr(fund, "fund_name")

                # fund_name = fund_name.replace(amc_unique, "")

                def m(x):
                    # scheme = x["Scheme"].replace(amc_unique, "")
                    # return fuzz.token_set_ratio(
                    #     fund_name, scheme) > 95

                    return fund_name == x["Scheme"]

                mask = df2.apply(lambda x: fund_name ==
                                 x["Scheme"], axis=1)

                df3 = df2[mask]
                # df3 = df2[df2.apply()]
                # print(df3)

                if len(df3.index) > 0:
                    df2.drop(labels=df3.index, axis=0, inplace=True)
                    print("fund name", fund_name)
                    df3 = df3.drop_duplicates(subset="Total TER", keep="last")
                    print(df3)
                else:
                    print("fund name not found or some other error", fund_name)
                    scheme_not_found.append(fund_name)

                # break
            print(scheme_not_found)
            print(df2.shape)
            # for row in df2.itertuples():
            #     print(row)

        else:
            print("unable to identify amc!")
    else:
        print(col_indexes)
        print("columns not present unable to parse")


def identify_amc(df):

    amcs = get_amc_common_names()

    df3 = df.drop_duplicates(subset="Scheme", keep="last")

    df3 = df3.head(15)

    schemes = df3.loc[:, "Scheme"].values

    amc_score = {}

    for amc_name in amcs:
        for scheme_name in schemes:
            ratio = fuzz.token_set_ratio(amc_name, scheme_name)
            if ratio > 95:
                if amc_name in amc_score:
                    amc_score[amc_name] += 1
                else:
                    amc_score[amc_name] = 1
                break

    max_score = 0
    final_amc = None

    for key in amc_score:
        if amc_score[key] > max_score:
            final_amc = key

    if final_amc is not None:
        return AMC.objects.match_amc_with_short_name(final_amc), final_amc
    else:
        return None, None


def find_head_row(df):
    # most of our logic is based on scheme in row
    # this row is most important is present in all excel sheet

    expected_cols = ["Scheme", "Date", "Total TER"]

    # for col in expected_cols:
    mask = df.apply(lambda x: x.astype(str).str.contains('scheme', False))
    df1 = df[mask.any(axis=1)]
    indexes = df1.index.values

    col_indexes = {}

    if len(indexes) > 0:
        index = indexes[0]
        base_row_index = index

        col_indexes["row_index"] = base_row_index

        base_row = df.iloc[index].to_numpy()

        # Total TER is special columun and it will repeat muliptle times
        # mainly because of direct/regular/etc plans
        # 99% cases the 1st is regular, 2nd is direct
        # code below is based on that assumption

        ter_occurance = 0

        indexes = []
        for col in expected_cols:
            i = 0
            for val in base_row:
                ratio = fuzz.token_set_ratio(col, val)
                # print(ratio, "==", col, val)
                if col in val or ratio > 95:
                    # i = list(base_row).index(val)
                    indexes.append(i)

                    if col == "Total TER" and ter_occurance > 1:
                        continue

                    col_indexes[col] = i
                    if col == "Total TER":
                        ter_occurance += 1
                    if col != "Total TER":
                        break
                i += 1

        col_indexes["indexes"] = indexes

        print(col_indexes)
    return col_indexes
