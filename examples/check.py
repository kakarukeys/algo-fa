import numpy as np
from pandas.parser import CParserError

from fa.archive.load import load_historical_data, load_financial_data, FINANCIAL_REPORT_TYPES
from fa.analysis.sanity import check_for_missing_date, check_for_discontinuity, check_for_missing_value

from settings import archive_directory, symbols


""" Perform sanity check on all the data in the archive """

def print_missing_dates(result):
    print("missing dates: ", end='')
    if result:
        for date in result:
            print("Missing date before {0}.".format(date))
    else:
        print("No missing date.")
    print()

def print_missing_values(result):
    print("missing values: ", end='')
    if result.empty:
        print("No missing value.")
    else:
        print()
        print(result)
    print()

def print_discontinuity(result):
    print("discontinuity: ", end='')
    if result.empty:
        print("No discontinuity.")
    else:
        print()
        print(result)
    print()

if __name__ == "__main__":
    for s in symbols:
        print("Symbol: {0}\n".format(s))
        print("historical")
        print("----------")

        try:
            df = load_historical_data(archive_directory, s)
        except CParserError as e:
            print("Error during parsing. " + str(e))
            print()
        except Exception as e:
            msg = str(e)
            if msg == "Integer column has NA values":
                print("Error during parsing. " + msg)
                print()
            else:
                raise
        else:
            print_missing_dates(check_for_missing_date(df, np.timedelta64(5, 'D')))
            print_missing_values(check_for_missing_value(df))
            print_discontinuity(check_for_discontinuity(df, 6))

        for report_type in FINANCIAL_REPORT_TYPES:
            print(report_type)
            print("----------------")

            try:
                df = load_financial_data(archive_directory, report_type, s)
            except ValueError as e:
                print("Error during parsing. " + str(e))
                print()
            else:
                print_missing_dates(check_for_missing_date(df, np.timedelta64(366, 'D')))
                print_missing_values(check_for_missing_value(df))
                print_discontinuity(check_for_discontinuity(df, 2))
