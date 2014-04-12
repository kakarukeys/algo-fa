import numpy as np
from pandas.parser import CParserError

from fa.loader import load_historical_data, load_financial_data, FINANCIAL_REPORT_TYPES
from fa.sanity import check_for_missing_date

from settings import archive_directory, symbols


""" Perform sanity check on all the data in the archive """

def print_result(result):
    for date in result:
        print("Missing date before {0}.".format(date))
    else:
        print("No missing date.")

if __name__ == "__main__":
    for s in symbols:
        print("Symbol: " + s)
        print("historical: ", end='')

        try:
            df = load_historical_data(archive_directory, s)
        except CParserError as e:
            print("Error during parsing. " + str(e))
        else:
            print_result(check_for_missing_date(df, np.timedelta64(34, 'D')))

        for report_type in FINANCIAL_REPORT_TYPES:
            print(report_type + ": ", end='')

            try:
                df = load_financial_data(archive_directory, report_type, s)
            except ValueError as e:
                print("Error during parsing. " + str(e))
            else:
                print_result(check_for_missing_date(df, np.timedelta64(366, 'D')))

        print()
