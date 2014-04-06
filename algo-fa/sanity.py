from loader import load_historical_data, load_financial_data, FINANCIAL_REPORT_TYPES
from settings import archive_directory, symbols

import numpy as np


def check_for_missing_date(df, tolerance):
    """ Returns a series (date -> diff with previous date) where the diff is greater than a tolerance
        df: DataFrame which index is dates
        tolerance: numpy.timedelta64 object.
    """
    dates = df.index.to_series()
    date_change = dates - dates.shift(1)
    return date_change[date_change > tolerance]

def print_result(result):
    if result.empty:
        print("No missing date.")
    else:
        for date in result.index:
            print("Missing date before {0}.".format(date))

if __name__ == "__main__":
    for s in symbols:
        print("Symbol: " + s)
        print("historical: ", end='')

        df = load_historical_data(archive_directory, s)
        print_result(check_for_missing_date(df, np.timedelta64(34, 'D')))

        for report_type in FINANCIAL_REPORT_TYPES:
            print(report_type + ": ", end='')

            df = load_financial_data(archive_directory, report_type, s)
            print_result(check_for_missing_date(df, np.timedelta64(366, 'D')))

        print()
