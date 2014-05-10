import unittest

import pandas as pd
import numpy as np

from fa.analysis import sanity
from tests.util import PandasTestCase


class TestSanity(PandasTestCase):
    def test_check_for_missing_date(self):
        frame = pd.Series([1, 2, 3], index=pd.to_datetime(["2012-12-21", "2012-12-23", "2012-12-24"]))
        result = sanity.check_for_missing_date(frame, np.timedelta64(1, 'D'))
        self.assertEqual(result, pd.to_datetime(["2012-12-23"]))

    def test_check_for_missing_value(self):
        df = pd.DataFrame({'a': [1, 2, 3, 4], 'b': [2, np.nan, 3, 4], 'c': [3, 2, np.nan, 2], 'd': [1, 2, 3, np.nan]})

        result = sanity.check_for_missing_value(df)

        self.assertFrameEqual(
            result,
            pd.DataFrame({'b': [np.nan, 3, 4], 'c': [2, np.nan, 2], 'd': [2, 3, np.nan]}, index=[1, 2, 3])
        )

    def test_is_outlier(self):
        frame = pd.Series([2] * 100 + [0, 1.42, 2.58, 4])
        # 2-sigma, mean, 2-sigma: 1.42, 2, 2.58
        result = sanity.is_outlier(frame, 2)
        self.assertFrameEqual(result, pd.Series([False] * 100 + [True, False, False, True]))

        frame = pd.DataFrame({'a': [1, 2, 4], 'b': [3, 2, 1]})
        # std dev ~= 1.53
        result = sanity.is_outlier(frame, 1)
        self.assertFrameEqual(result, pd.DataFrame({'a': [False, False, True], 'b': [False, False, False]}))

    def test_check_for_discontinuity(self):
        df = pd.DataFrame({
            'a': [1, 2, 100, 101, 102],
            'b': [1, 2, 3, 4, 100],
            'c': [1, 2, 3, 4, 5],
        })

        result = sanity.check_for_discontinuity(df, 1)

        self.assertFrameEqual(result, pd.DataFrame({
            'a': [2, np.nan],
            'b': [np.nan, 4],
        }, index=[1, 3]))

    def test_check_for_discontinuity__DatetimeIndex(self):
        df = pd.DataFrame({
            'a': [1, 2, 100, 101, 102],
            'b': [1, 2, 3, 4, 100],
            'c': [1, 2, 3, 4, 5],
        }, index=pd.date_range("2012-01-01", periods=5))

        result = sanity.check_for_discontinuity(df, 1)

        self.assertFrameEqual(result, pd.DataFrame({
            'a': [2, np.nan],
            'b': [np.nan, 4],
        }, index=pd.to_datetime(["2012-01-02", "2012-01-04"])))

if __name__ == "__main__":
    unittest.main()
