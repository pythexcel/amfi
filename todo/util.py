from math import ceil, floor
import pandas as pd

import re

# this function expects a json data from db or any other source.
# two main fields are required date, nav there can more fields as well

# this will return a date frame with index as date and value is nav


def clean_fund_string(name):
    name = re.sub("[\(\[].*?[\)\]]", "", name)
    name = re.sub(' +', ' ', name)
    name = name.replace("and", "&")
    name = name.replace("And", "&")
    name = name.replace(" Direct", "")
    name = name.replace(" Growth", "")
    name = name.replace(" - ", " ")
    name = name.replace("-", " ")
    name = name.replace(".", "")
    name = name.replace("#","")
    # add space because some fund name has plan in there name itself
    name = name.replace(" Plan ", "")

    

    name = name.strip()
    name = name.lower()

    # remove plan if its last word of scheme
    if name.split()[-1] == "plan":
        # this issue came with Mahindra Mutual Fund Kar Bachat Yojana Direct Plan
        name = ' '.join(name.split(' ')[:-1])
    return name


def get_priceindex_data(input):
    df = pd.DataFrame(input, columns=["close", "date"])
    df['Datetime'] = pd.to_datetime(df["date"])
    df = df.set_index("Datetime")
    return df


def get_date_index_data(input):
    df = pd.DataFrame(input, columns=["nav", "date"])
    df['Datetime'] = pd.to_datetime(df["date"])
    df = df.set_index("Datetime")
    return df


def fill_date_frame_data(df, start_date, end_date, method='ffill'):
    idx = pd.date_range(start_date, end_date)
    df = df.reindex(idx, method=method)
    return df


def float_round(num, places=0, direction=floor):
    return direction(num * (10**places)) / float(10**places)


def cagr(initial, final, years, months=None):
    """
    Compound Annual Growth Rate, given an initial and a final value for an investment,
    as well as the time elapsed (in years or fractions of years)
    """
    initial = float(initial)
    final = float(final)

    if years is not None:
        years = float(years)
    else:
        years = float(months) / 12.0

    if initial == 0:
        raise Exception('The initial value cannot be zero')

    if years == 0:
        raise Exception('The time period cannot be zero')

    return (final / initial) ** (1.0 / years) - 1
