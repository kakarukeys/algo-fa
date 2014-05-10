import unittest
import pandas as pd
from tests import util


class TestPandasTestCase(unittest.TestCase):
    def test_assertFrameEqual__Series(self):
        ptc = util.PandasTestCase()

        ptc.assertFrameEqual(pd.Series([1,2,3]), pd.Series([1,2,3]))
        self.assertRaises(AssertionError, ptc.assertFrameEqual, pd.Series([1,2,4]), pd.Series([1,2,3]))

    def test_assertFrameEqual__DataFrame(self):
        ptc = util.PandasTestCase()

        ptc.assertFrameEqual(pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]}), pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]}))
        self.assertRaises(
            AssertionError,
            ptc.assertFrameEqual,
            pd.DataFrame({'a': [1,2,4], 'b': [4,5,6]}),
            pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
        )

        # Can only compare identically-labeled DataFrame objects
        self.assertRaises(
            AssertionError,
            ptc.assertFrameEqual,
            pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]}),
            pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]}, index=[6,7,8])
        )

    def test_assertFrameEqual__Panel(self):
        ptc = util.PandasTestCase()
        df1 = pd.DataFrame({'a': [1,2,3], 'b': [4,5,6]})
        df2 = pd.DataFrame({'a': [1,2,4], 'b': [4,5,6]})
        p1 = pd.Panel({'A': df1, 'B': df1})
        p2 = pd.Panel({'A': df1, 'B': df1})
        p3 = pd.Panel({'A': df2, 'B': df1})

        self.assertRaises(NotImplementedError, ptc.assertFrameEqual, p1, p2)
        self.assertRaises(NotImplementedError, ptc.assertFrameEqual, p3, p2)
