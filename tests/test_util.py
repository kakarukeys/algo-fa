import unittest
from unittest.mock import patch, MagicMock
from io import StringIO
import os

import pandas as pd
import peewee as pw

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

class TestFileIOTestCase(unittest.TestCase):
    def test_setUp(self):
        real_open = open

        # check if open is patched after setUp runs
        ftc = test_util.FileIOTestCase()
        ftc.setUp()

        with open("file.txt", 'r') as f:
            f.read()

        ftc.mo.assert_called_once_with("file.txt", 'r')
        ftc.mo.return_value.read.assert_called_once_with()

        # check if the patching is undone in cleanup
        ftc.doCleanups()
        self.assertIs(open, real_open)

    def test_get_written_string(self):
        ftc = test_util.FileIOTestCase()
        ftc.setUp()

        with open("file.txt", 'w') as f:
            f.write("abc\n")
            f.write("def\n")

        self.assertEqual(ftc.get_written_string(), "abc\ndef\n")

        ftc.doCleanups()

class TestDBTestCase(unittest.TestCase):
    def test_setUpClass_tearDownClass(self):
        mock_test_db = pw.SqliteDatabase(None)

        class MockModel(pw.Model):
            name = pw.CharField()

            class Meta:
                database = mock_test_db

        with patch("fa.database.models.db", mock_test_db), \
             patch("fa.database.models.export", [MockModel]):
            test_util.DBTestCase.setUpClass()

        try:
            MockModel.create(name="foo")
            MockModel.get()
        except pw.OperationalError:
            self.fail("table not created!")

        # assert this after a query: creation of database is lazy, deferred till actual query happens
        self.assertTrue(os.path.exists(test_util.DBTestCase.test_db_path))

        with patch("fa.database.models.db", mock_test_db), \
             patch("fa.database.models.export", [MockModel]):
            test_util.DBTestCase.tearDownClass()

        self.assertTrue(mock_test_db.is_closed())
        self.assertFalse(os.path.exists(test_util.DBTestCase.test_db_path))

    def test_setUpClass_cleanup(self):
        with patch("fa.database.models.db.init", MagicMock(side_effect=Exception)), \
             patch("tests.util.DBTestCase._cleanup") as mock_cleanup:
            try:
                test_util.DBTestCase.setUpClass()
            except:
                mock_cleanup.assert_called_once_with()

class TestFAUtil(unittest.TestCase):
    def test_transpose_items(self):
        transposed = fa_util.transpose_items((("foo", [1, 2, 3]), ("bar", [4, 5, 6])))
        self.assertEqual(list(transposed), [("foo", "bar"), (1, 4), (2, 5), (3, 6)])

    def test_transpose_csv(self):
        output = StringIO()
        fa_util.transpose_csv(StringIO("foo|bar\n1|4.0\n2|5\n3|6\n"), output, '|')
        self.assertEqual(output.getvalue(), "foo|1|2|3\r\nbar|4.0|5|6\r\n")

    def test_chucks(self):
        l = list(range(10))
        chunks = list(fa_util.partition(l, 4))
        self.assertEqual(chunks, [[0, 1, 2 ,3], [4, 5, 6, 7], [8, 9]])

if __name__ == "__main__":
    unittest.main()
