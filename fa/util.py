import csv


def transpose_items(items):
    """ >>> list(transpose_items((("foo", [1, 2, 3]), ("bar", [4, 5, 6]))))
        [('foo', 'bar'), (1, 4), (2, 5), (3, 6)]
    """
    columns = ([column_name] + values for column_name, values in items)
    return zip(*columns)

def transpose_csv(csv_file, output, delimiter):
    """ Transposes the content of <csv_file> and writes to <output>
        csv_file, output: file-like objects
        delimiter: the symbol that separates the column values
    """
    reader = csv.reader(csv_file, delimiter=delimiter)
    writer = csv.writer(output, delimiter=delimiter)
    writer.writerows(zip(*reader))
