import pandas as pd

# this function expects a json data from db or any other source.
# two main fields are required date, nav there can more fields as well

# this will return a date frame with index as date and value is nav


def get_date_index_data(input):
    df = pd.DataFrame(input, columns=["nav", "date"])
    df['Datetime'] = pd.to_datetime(df["date"])
    df = df.set_index("Datetime")
    return df


def fill_date_frame_data(df, start_date, end_date, method='ffill'):
    idx = pd.date_range(start_date, end_date)
    df = df.reindex(idx, method=method)
    return df

from math import ceil, floor
def float_round(num, places = 0, direction = floor):
    return direction(num * (10**places)) / float(10**places)