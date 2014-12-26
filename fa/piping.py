import csv
from io import StringIO

from fa.util import to_pythonic_name


def csv_rows_to_records(symbol, csv_rows):
    """ Returns a generator of database records that come from every row in <csv_rows>,
        with <symbol> added and the keys of each record being the pythonic version of column names.

        symbol: a string,
        csv_row: an iterator of csv rows (tuples), first row must be headers.
    """
    keys = [to_pythonic_name(verbose_name) for verbose_name in next(csv_rows)]  # headers to keys
    for row in csv_rows:
        record = dict(zip(keys, row))
        record["symbol_obj"] = symbol
        yield record

def csv_string_to_records(symbol, csv_string, **kwargs):
    """ Returns a generator of database records that come from every row in <csv_string>,
        with <symbol> added and the keys of each record being the pythonic version of column names.

        symbol: a string,
        csv_string: comma delimited, with headers,
        extra keyword arguments are passed on to Reader.
    """
    reader = csv.reader(StringIO(csv_string), **kwargs)
    yield from csv_rows_to_records(symbol, reader)
