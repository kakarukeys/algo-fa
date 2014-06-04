import unittest
from unittest.mock import patch, MagicMock
from io import StringIO

import pandas as pd

from tests import util as test_util
from fa import util as fa_util


class TestPandasTestCase(unittest.TestCase):
    def test_assertFrameEqual__Series(self):
        ptc = test_util.PandasTestCase()
        s1 = pd.Series()
        s2 = pd.Series()

        with patch("tests.util.assert_series_equal") as mock_assert_series_equal:
            ptc.assertFrameEqual(s1, s2, b=1)
            mock_assert_series_equal.assert_called_once_with(s1, s2, b=1)

        with patch("tests.util.assert_series_equal", MagicMock(side_effect=AssertionError)) as mock_assert_series_equal:
            self.assertRaises(AssertionError, ptc.assertFrameEqual, s1, s2)

    def test_assertFrameEqual__DataFrame(self):
        ptc = test_util.PandasTestCase()
        df1 = pd.DataFrame()
        df2 = pd.DataFrame()

        with patch("tests.util.assert_frame_equal") as mock_assert_frame_equal:
            ptc.assertFrameEqual(df1, df2, b=1)
            mock_assert_frame_equal.assert_called_once_with(df1, df2, b=1)

    def test_assertFrameEqual__Panel(self):
        ptc = test_util.PandasTestCase()
        p1 = pd.Panel()
        p2 = pd.Panel()

        with patch("tests.util.assert_panel_equal") as mock_assert_panel_equal:
            ptc.assertFrameEqual(p1, p2, b=1)
            mock_assert_panel_equal.assert_called_once_with(p1, p2, b=1)

class TestFAUtil(unittest.TestCase):
    def test_transpose_items(self):
        transposed = fa_util.transpose_items((("foo", [1, 2, 3]), ("bar", [4, 5, 6])))
        self.assertEqual(list(transposed), [("foo", "bar"), (1, 4), (2, 5), (3, 6)])

    def test_transpose_csv(self):
        output = StringIO()
        fa_util.transpose_csv(StringIO("foo|bar\n1|4\n2|5\n3|6\n"), output, '|')
        self.assertEqual(output.getvalue(), "foo|1|2|3\r\nbar|4|5|6\r\n")

if __name__ == "__main__":
    unittest.main()
