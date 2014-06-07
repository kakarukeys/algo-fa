import csv, json, os

import pandas as pd


def write_file(obj, directory, symbol):
    """ Writes <obj> to a file <symbol>.{extension} in <directory>, extension is either csv or json.
        obj is one of these:
            a dictionary (json object)
            a csv string
            a DataFrame object
            an iterable of csv rows
    """
    if isinstance(obj, dict):
        extension = "json"
        write = json.dump
    elif isinstance(obj, str):
        extension = "csv"
        write = lambda obj, f: f.write(obj)
    elif isinstance(obj, pd.DataFrame):
        extension = "csv"
        write = lambda obj, f: obj.to_csv(f, sep='|', na_rep="nan")
    else:
        extension = "csv"
        write = lambda obj, f: csv.writer(f, delimiter='|').writerows(obj)

    filepath = os.path.join(directory, symbol + '.' + extension)

    with open(filepath, 'w') as f:
        write(obj, f)

def dump(data, archive_directory, table_name):
    """ For each symbol, object pair in <data>'s items, writes the object to a file in <archive_directory>/<table_name>.

        data: {"symbol": object}
    """
    directory = os.path.join(archive_directory, table_name)

    if not os.path.exists(directory):
        os.makedirs(directory)

    for symbol, obj in data.items():
        write_file(obj, directory, symbol)
