import csv
from io import StringIO

from fa.util import to_pythonic_name


def csv_string_to_records(symbol, csv_string, **kwargs):
    """ Returns a generator of database records that come from every row in <csv_string>,
        with <symbol> added and the keys of each record being the pythonic version of column names.

        symbol: a string,
        csv_string: comma delimited, with headers,
        extra keyword arguments are passed on to Reader.
    """
    reader = csv.reader(StringIO(csv_string), **kwargs)
    keys = [to_pythonic_name(verbose_name) for verbose_name in next(reader)]  # headers to keys
    for row in reader:
        record = dict(zip(keys, row))
        record["symbol_obj"] = symbol
        yield record
