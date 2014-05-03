import unittest

import pandas as pd
from pandas.tseries.frequencies import YearBegin, QuarterBegin
import numpy as np

from fa.analysis import inspect


class TestInspect(unittest.TestCase):
    def test_get_first_commonly_available_year(self):
        yb = YearBegin()
        n = np.nan

        timeseries_coll = [
            pd.Series([1, 2, 3, 4], index=pd.date_range('2000-01-01', periods=4, freq=yb)),
            pd.Series(   [2, 3, 4], index=pd.date_range('2001-01-01', periods=3, freq=yb)),
            pd.Series(      [n, 4], index=pd.date_range('2002-01-01', periods=2, freq=yb)),
            pd.Series(         [4], index=pd.date_range('2003-01-01', periods=1, freq=yb)),
        ]

        self.assertEqual(inspect.get_first_commonly_available_year(timeseries_coll, 0.25), 2000)
        self.assertEqual(inspect.get_first_commonly_available_year(timeseries_coll, 0.26), 2001)
        self.assertEqual(inspect.get_first_commonly_available_year(timeseries_coll, 0.5), 2001)
        self.assertEqual(inspect.get_first_commonly_available_year(timeseries_coll, 0.51), 2003)

    def test_get_first_commonly_available_year__smaller_freq(self):
        qb = QuarterBegin()
        n = np.nan

        timeseries_coll = [
            pd.Series([n, n, n, 4], index=pd.date_range('2000-01-01', periods=4, freq=qb)),
            pd.Series(   [n, n, 4], index=pd.date_range('2000-04-01', periods=3, freq=qb)),
            pd.Series(      [n, 4], index=pd.date_range('2000-07-01', periods=2, freq=qb)),
            pd.Series(         [4], index=pd.date_range('2000-10-01', periods=1, freq=qb)),
        ]

        self.assertEqual(inspect.get_first_commonly_available_year(timeseries_coll), 2000)

    def test_get_first_commonly_available_year__NA(self):
        yb = YearBegin()
        n = np.nan

        timeseries_coll = [
            pd.Series([1, 2, 3, 4], index=pd.date_range('2000-01-01', periods=4, freq=yb)),
            pd.Series(   [2, 3, 4], index=pd.date_range('2001-01-01', periods=3, freq=yb)),
            pd.Series(      [n, 4], index=pd.date_range('2002-01-01', periods=2, freq=yb)),
            pd.Series(         [n], index=pd.date_range('2003-01-01', periods=1, freq=yb)),
        ]

        self.assertEqual(inspect.get_first_commonly_available_year(timeseries_coll), None)

if __name__ == "__main__":
    unittest.main()
