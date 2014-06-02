def transpose_items(items):
    """ >>> list(transpose_items((("foo", [1, 2, 3]), ("bar", [4, 5, 6]))))
        [('foo', 'bar'), (1, 4), (2, 5), (3, 6)]
    """
    columns = ([column_name] + values for column_name, values in items)
    return zip(*columns)
