import unittest
from pandas.core.generic import NDFrame
from pandas import Panel


class PandasTestCase(unittest.TestCase):
    """ For test case with assertion involving Pandas frame objects """
    def assertFrameEqual(self, first, second, msg=None):
        """ Fail if the two frames are unequal at all values as determined by the '==' operator. """
        if isinstance(first, Panel):
            raise NotImplementedError("assertFrameEqual can't compare Panel objects yet!")

        e = self.failureException(msg or "\n{0}\n!=\n{1}".format(first, second))

        try:
            is_equal = first == second
        except ValueError as ve:
            if str(ve) == "Can only compare identically-labeled DataFrame objects":
                raise e
            else:
                raise

        while isinstance(is_equal, NDFrame):
            is_equal = is_equal.all()

        if not is_equal:
            raise e
