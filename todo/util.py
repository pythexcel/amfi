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


maping_dict =[ {"benchmark_name":"S&P BSE 150 MidCap","benchmark":"SPB15MIP"},
                {"benchmark_name":"S&P BSE SENSEX","benchmark":"SENSEX"},
                {"benchmark_name":"S&P BSE AllCap","benchmark":"SPBSAIP"},
                {"benchmark_name":"S&P BSE Enhanced Value","benchmark":"SPBSEVIP"},
                {"benchmark_name":"S&P BSE Teck","benchmark":"SIBTEC"},
                {"benchmark_name":"S&P BSE 500","benchmark":"BSE500"},
                {"benchmark_name":"S&P BSE 200","benchmark":"BSE200"},
                {"benchmark_name":"S&P BSE 100","benchmark":"BSE100"},
                {"benchmark_name":"S&P BSE Small Cap","benchmark":"BSESML"},
                {"benchmark_name":"S&P BSE HC","benchmark":"SI0800"},
                {"benchmark_name":"S&P BSE Sensex","benchmark":"SENSEX"},
                {"benchmark_name":"S&P 500 International","benchmark":"BSE500"},
                {"benchmark_name":"S&P BSE Information Technology","benchmark":"SI1000"},
                {"benchmark_name":"S&P 500","benchmark":"BSE500"},
                {"benchmark_name":"S&P BSE IT","benchmark":"SI1000"},
                {"benchmark_name":"S&P BSE BANKEX","benchmark":"SIBANK"},
                {"benchmark_name":"S&P BSE 500 Shariah","benchmark":"SPBSE5S"},
                {"benchmark_name":"S&P BSE India Infrastructure","benchmark":"INFRA"},
                {"benchmark_name":"S&P BSE Teck","benchmark":"SIBTEC"},
                {"benchmark_name":"S&P BSE Mid Cap","benchmark":"BSEMID"},
                {"benchmark_name":"S&P BSE 250 Large MidCap","benchmark":"SPB25XIP"},
                {"benchmark_name":"S&P BSE Healthcare","benchmark":"SI0800"},
                {"benchmark_name":"S&P BSE 50","benchmark":"SPBSS5IP"},
                {"benchmark_name":"S&P BSE Midcap","benchmark":"BSEMID"},
                {"benchmark_name":"S&P BSE Health Care","benchmark":"SI0800"},
                {"benchmark_name":"S&P BSE 250 Small Cap","benchmark":"SPB25SIP"},
                {"benchmark_name":"S&P BSE PSU","benchmark":"SIBPSU"},
                {"benchmark_name":"S&P BSE HEALTH CARE","benchmark":"SI0800"},
                {"benchmark_name":"S&P BSE PSU","benchmark":"SIBPSU"},

                {"benchmark_name":"NIFTY 50","benchmark":"NIFTY 50"},
                {"benchmark_name":"NIFTY NEXT 50","benchmark":"NIFTY NEXT 50"},
                {"benchmark_name":"NIFTY SMLCAP 100","benchmark":"NIFTY SMLCAP 100"},
                {"benchmark_name":"NIFTY MIDCAP 100","benchmark":"NIFTY MIDCAP 100"},
                {"benchmark_name":"NIFTY 100","benchmark":"NIFTY 100"},
                {"benchmark_name":"NIFTY 500","benchmark":"NIFTY 500"},
                {"benchmark_name":"NIFTY 200","benchmark":"NIFTY 200"},
                {"benchmark_name":"NIFTY MIDCAP 150","benchmark":"NIFTY MIDCAP 150"},
                {"benchmark_name":"NIFTY FMCG","benchmark":"NIFTY FMCG"},
                {"benchmark_name":"NIFTY MNC","benchmark":"NIFTY MNC"},
                {"benchmark_name":"NIFTY INFRA","benchmark":"NIFTY INFRA"},
                {"benchmark_name":"NIFTY MIDCAP 50","benchmark":"NIFTY MIDCAP 50"},
                {"benchmark_name":"NIFTY FULL MIDCAP 100","benchmark":"NIFTY FULL MIDCAP 100"},
                {"benchmark_name":"NIFTY SMLCAP 250","benchmark":"NIFTY SMLCAP 250"},
                {"benchmark_name":"NIFTY SMLCAP 50","benchmark":"NIFTY SMLCAP 50"},
                {"benchmark_name":"NIFTY DIVIDEND OPPORTUNITIES 50","benchmark":"NIFTY DIVIDEND OPPORTUNITIES 50"},
                {"benchmark_name":"NIFTY INDIA CONSUMPTION","benchmark":"NIFTY INDIA CONSUMPTION"},
                {"benchmark_name":"NIFTY COMMODITIES","benchmark":"NIFTY COMMODITIES"},
                {"benchmark_name":"NIFTY MIDSMALLCAP 400","benchmark":"NIFTY MIDSMLCAP 400"},
                {"benchmark_name":"NIFTY FULL SMLCAP 100","benchmark":"NIFTY FULL SMLCAP 100"},
                {"benchmark_name":"NIFTY FINANCIAL SERVICES","benchmark":"NIFTY FINANCIAL SERVICES"},
                {"benchmark_name":"NIFTY LARGEMIDCAP 250","benchmark":"NIFTY LARGEMIDCAP 250"}         
]
