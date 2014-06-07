import unittest
from unittest.mock import patch, call
import os

import pandas as pd
import numpy as np

from fa.archive import save
from tests.util import FileIOTestCase


class TestWriteFile(FileIOTestCase):
    def test_write_file__json(self):
        with patch("fa.archive.save.json.dump") as mock_dump:
            save.write_file({"symbol": "C6L"}, "directory", "C6L")
            mock_dump.assert_called_once_with({"symbol": "C6L"}, self.mo.return_value)

        self.mo.assert_called_once_with(os.path.join("directory", "C6L.json"), 'w')

    def test_write_file__csv(self):
        save.write_file("a,b\n1,2", "directory", "C6L")

        self.mo.assert_called_once_with(os.path.join("directory", "C6L.csv"), 'w')
        self.assertEqual(self.get_written_string(), "a,b\n1,2")

    def test_write_file__DataFrame(self):
        df = pd.DataFrame({'a': [1.0, np.nan], 'b': [2, 4]})

        with patch("pandas.DataFrame.to_csv") as mock_to_csv:
            save.write_file(df, "directory", "C6L")
            mock_to_csv.assert_called_once_with(self.mo.return_value, sep='|', na_rep="nan")

        self.mo.assert_called_once_with(os.path.join("directory", "C6L.csv"), 'w')

        # Below test code doesn't work due to a bug in Pandas
        # save.write_file(df, "directory", "C6L")
        # self.assertEqual(self.get_written_string(), "|a|b\n0|1.0|2\n1|nan|4\n")

    def test_write_file__csv_rows(self):
        save.write_file((('a', 'b'), (1, 2)), "directory", "C6L")

        self.mo.assert_called_once_with(os.path.join("directory", "C6L.csv"), 'w')
        self.assertEqual(self.get_written_string(), "a|b\r\n1|2\r\n")

class TestDump(unittest.TestCase):
    def setUp(self):
        self.archive_directory = os.path.join(os.path.dirname(__file__), "fixture_data", "test_archive")

    def test_dump(self):
        with patch("fa.archive.save.write_file") as mock_write_file, \
             patch("os.makedirs") as mock_makedirs:

            save.dump({
                "C6L": {"symbol": "C6L"},
                "B2F": {"symbol": "B2F"},
            }, self.archive_directory, "wsj")

            directory = os.path.join(os.path.dirname(__file__), "fixture_data", "test_archive", "wsj")
            self.assertTrue(not mock_makedirs.called)
            mock_write_file.assert_has_calls([
                call({"symbol": "C6L"}, directory, "C6L"),
                call({"symbol": "B2F"}, directory, "B2F")
            ], any_order=True)

    def test_dump__new_directory(self):
        with patch("fa.archive.save.write_file"), \
             patch("os.makedirs") as mock_makedirs:

            save.dump({
                "C6L": {"symbol": "C6L"},
                "B2F": {"symbol": "B2F"},
            }, self.archive_directory, "xyzabc")

            directory = os.path.join(os.path.dirname(__file__), "fixture_data", "test_archive", "xyzabc")
            mock_makedirs.assert_called_once_with(directory)

if __name__ == "__main__":
    unittest.main()
