import unittest
from unittest.mock import patch, MagicMock

import pandas as pd
import numpy as np

from tests import util


class TestPandasTestCase(unittest.TestCase):
    def test_assertFrameEqual__Series(self):
        ptc = util.PandasTestCase()
        s1 = pd.Series()
        s2 = pd.Series()

        with patch("tests.util.assert_series_equal") as mock_assert_series_equal:
            ptc.assertFrameEqual(s1, s2, b=1)
            mock_assert_series_equal.assert_called_once_with(s1, s2, b=1)

        with patch("tests.util.assert_series_equal", MagicMock(side_effect=AssertionError)) as mock_assert_series_equal:
            self.assertRaises(AssertionError, ptc.assertFrameEqual, s1, s2)

    def test_assertFrameEqual__DataFrame(self):
        ptc = util.PandasTestCase()
        df1 = pd.DataFrame()
        df2 = pd.DataFrame()

        with patch("tests.util.assert_frame_equal") as mock_assert_frame_equal:
            ptc.assertFrameEqual(df1, df2, b=1)
            mock_assert_frame_equal.assert_called_once_with(df1, df2, b=1)

    def test_assertFrameEqual__Panel(self):
        ptc = util.PandasTestCase()
        p1 = pd.Panel()
        p2 = pd.Panel()

        with patch("tests.util.assert_panel_equal") as mock_assert_panel_equal:
            ptc.assertFrameEqual(p1, p2, b=1)
            mock_assert_panel_equal.assert_called_once_with(p1, p2, b=1)
