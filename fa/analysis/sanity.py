import numpy as np
from pandas.tseries.index import DatetimeIndex

from fa.calculator import backward_delta, derivative


def check_for_missing_date(df, tolerance):
    """ Returns a collection of dates where the diff with previous date is greater than a tolerance.
        df: DataFrame object which index contains the dates to be checked.
        tolerance: numpy.timedelta64 object.
    """
    dates = df.index.to_series()
    date_change = backward_delta(dates)
    return date_change[date_change > tolerance].index

def check_for_missing_value(df):
	""" Returns rows and columns of <df> that contain one or more missing values. """
	missing_values = np.isnan(df)
	return df.loc[missing_values.any(axis=1), missing_values.any(axis=0)]

def is_outlier(df, tolerance):
	""" test whether each value of <df> deviates from the mean of the column by <tolerance> * sigma """
	return np.abs(df - df.mean()) > df.std() * tolerance

def check_for_discontinuity(df, tolerance):
	""" Returns a DataFrame object containing only rows and columns with values of <df>
		at which there is an outlier first-order derivative.
		Normal values are set to NaN.

		tolerance: used in outlier test for first-order derivative, how many sigmas?
	"""
	if isinstance(df.index, DatetimeIndex):
		index_unit = np.timedelta64(365, 'D')	# doesn't matter what value, this is just for allowing the division to occur
	else:
		index_unit = 1

	der = derivative(df, index_unit)
	return df[is_outlier(der, tolerance)].dropna(axis=0, how="all").dropna(axis=1, how="all")
