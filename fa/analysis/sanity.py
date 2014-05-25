import numpy as np
from pandas.tseries.index import DatetimeIndex

from fa.calculator import backward_delta, derivative, get_deviations


def check_for_missing_date(frame, tolerance):
    """ Returns a collection of dates from <frame>'s index
        where the diff with previous date is greater than a tolerance.
        frame: Pandas NDFrame object which index is datetimes
        tolerance: numpy.timedelta64 object.
    """
    dates = frame.index.to_series()
    date_change = backward_delta(dates)
    return date_change[date_change > tolerance].index

def check_for_missing_value(df):
    """ Returns rows and columns of <df> that contain one or more missing values. """
    missing_values = np.isnan(df)
    return df.loc[missing_values.any(axis=1), missing_values.any(axis=0)]

def is_outlier(frame, tolerance):
    """ Tests whether each value of <frame> deviates from the mean of the column by more than <tolerance> * sigma
        frame: Series or DataFrame object
    """
    return np.abs(get_deviations(frame)) > tolerance

def check_for_discontinuity(df, tolerance):
    """ Returns a DataFrame object containing only rows and columns with values of <df>
        at which there is an outlier first-order partial derivative along row axis.
        Normal values are set to NaN.

        tolerance: used in outlier test for first-order derivative, how many sigmas?
    """
    if isinstance(df.index, DatetimeIndex):
        # doesn't matter what value, this is just for allowing the division to occur
        # result of is_outlier does not depend on index_unit
        index_unit = np.timedelta64(365, 'D')
    else:
        index_unit = 1

    der = derivative(df, index_unit)
    return df[is_outlier(der, tolerance)].dropna(axis=0, how="all").dropna(axis=1, how="all")
