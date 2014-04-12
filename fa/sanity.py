def check_for_missing_date(df, tolerance):
    """ Returns a series (date -> diff with previous date) where the diff is greater than a tolerance
        df: DataFrame which index is dates
        tolerance: numpy.timedelta64 object.
    """
    dates = df.index.to_series()
    date_change = dates - dates.shift(1)
    return date_change[date_change > tolerance]
