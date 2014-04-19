from itertools import count
import numpy as np


def get_first_commonly_available_year(timeseries_coll, availability=1):
	""" Returns the earliest year (integer) at which <availability> of all timeseries in <timeseries_coll> has a numeric value,
		returns None if not found.
		0 < availability <= 1, default: 1.
	"""
	start_date = min([ts.index[0] for ts in timeseries_coll])
	end_date = max([ts.index[-1] for ts in timeseries_coll])
	min_total_available_values = len(timeseries_coll) * availability

	for year in range(start_date.year, end_date.year + 1):
		counter = count(1)
		for ts in timeseries_coll:
			if not np.isnan(ts.get(str(year), np.nan)) and next(counter) >= min_total_available_values:
				return year
