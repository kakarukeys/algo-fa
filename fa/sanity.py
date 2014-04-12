def check_for_missing_date(df, tolerance):
    """ Returns a series (date -> diff of it with previous date) where the diff is greater than a tolerance
        df: DataFrame object which index contains the dates to be checked.
        tolerance: numpy.timedelta64 object.
    """
    dates = df.index.to_series()
    date_change = dates - dates.shift(1)
    return date_change[date_change > tolerance]
