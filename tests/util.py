import unittest
from unittest.mock import mock_open, patch
import os

from pandas import Series, DataFrame
from pandas.util.testing import assert_series_equal, assert_frame_equal, assert_panel_equal

from fa.database import models


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

class FileIOTestCase(unittest.TestCase):
    """ For testing code involving file io operations """
    def setUp(self):
        """ patches the open function with a mock, to be undone after test. """
        self.mo = mock_open()

        patcher = patch("builtins.open", self.mo)
        patcher.start()
        self.addCleanup(patcher.stop)

    def get_written_string(self):
        return ''.join(c[0][0] for c in self.mo.return_value.write.call_args_list)

class DBTestCase(unittest.TestCase):
    """ For testing code involving database io operations
        Note: this class interacts with models module
    """
    test_db_path = "test-algo-fa.db"

    @classmethod
    def _cleanup(cls):
        """ closes connection and deletes test database """
        models.db.close()
        os.remove(cls.test_db_path)

    @classmethod
    def setUpClass(cls):
        """ creates test database and all tables """
        try:
            models.db.init(cls.test_db_path)
            models.db.create_tables(models.export)
        except:
            cls._cleanup()   # immediately performs cleanup if exception occurs
            raise

    @classmethod
    def tearDownClass(cls):
        """ does cleanup after all tests """
        cls._cleanup()
