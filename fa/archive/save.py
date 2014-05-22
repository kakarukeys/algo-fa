import json
import os


def write_file(directory, symbol, datatype, obj):
    """ Writes <obj> to a file <symbol>.<datatype> in <directory>.
        datatype is either "csv" or "json".
    """
    filepath = os.path.join(directory, symbol + '.' + datatype)
    with open(filepath, 'w') as f:
        if datatype == "csv":
            f.write(obj)
        else:
            json.dump(obj, f)

def dump(data, archive_directory, table_name, datatype):
    """ Writes each value of <data> to <archive_directory>/<table_name>, under symbol name the key of the value,
        data type <datatype>.

        data: {"symbol": data_object}
        datatype is either "csv" or "json".
    """
    directory = os.path.join(archive_directory, table_name)

    if not os.path.exists(directory):
        os.makedirs(directory)

    for s, obj in data.items():
        write_file(directory, s, datatype, obj)
