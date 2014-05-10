import unittest

from pandas import Series, DataFrame
from pandas.util.testing import assert_series_equal, assert_frame_equal, assert_panel_equal


class PandasTestCase(unittest.TestCase):
    """ For test case with assertion involving Pandas NDFrame objects """
    def assertFrameEqual(self, first, second, msg=None, **kwargs):
        """ Fail if the two NDFrame objects of the same type are unequal at any value
            as determined by the '==' operator (two NaNs are treated as equal).

            It reuses assertion functions in pandas.util.testing internally, but produces
            clearer failure message.

            Any extra extra keyword arguments are passed on to the assertion function.
        """
        if isinstance(first, Series):
            assert_func = assert_series_equal
        elif isinstance(first, DataFrame):
            assert_func = assert_frame_equal
        else:
            assert_func = assert_panel_equal

        try:
            assert_func(first, second, **kwargs)
        except AssertionError:
            raise self.failureException(msg or "\n{0}\n!=\n{1}".format(first, second))
