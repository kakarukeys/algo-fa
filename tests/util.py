import unittest

class PandasTestCase(unittest.TestCase):
    """ For test case with assertion involving Pandas frame objects """
    def assertFrameEqual(self, first, second, msg=None):
        """ Fail if the two frames are unequal at all values as determined by the '==' operator. """
        if not (first == second).all():
            raise self.failureException(msg or "\n{0}\n!=\n{1}".format(first, second))
