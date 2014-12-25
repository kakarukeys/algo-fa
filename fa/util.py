import csv
import re


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

def to_pythonic_name(verbose_name):
    return re.sub(r"[^\w]+", '_', verbose_name).lower()

def partition(l, n):
    """ Yields successive n-sized chunks from list <l> """
    for i in range(0, len(l), n):
        yield l[i : i + n]

def assert_equal(actual, expected, name="The variable"):
    """ unless <actual> is equal to <expected>, raises AssertionError with a nice message """
    assert actual == expected, "{0} is expected to be {1} but is actually {2}".format(name, expected, actual)
