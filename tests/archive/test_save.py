import unittest
from unittest.mock import mock_open, patch, call
import os

from fa.archive import save


class TestSave(unittest.TestCase):
    def setUp(self):
        self.archive_directory = os.path.join(os.path.dirname(__file__), "fixture_data", "test_archive")

    def test_write_file__json(self):
        mo = mock_open()
        with patch("builtins.open", mo), \
             patch("fa.archive.save.json.dump") as mock_dump:

            save.write_file({"symbol": "C6L"}, "directory", "C6L")

            mo.assert_called_once_with(os.path.join("directory", "C6L.json"), 'w')
            mock_dump.assert_called_once_with({"symbol": "C6L"}, mo())

    def test_write_file__csv(self):
        mo = mock_open()
        with patch("builtins.open", mo):
            save.write_file("a,b\n1,2", "directory", "C6L")

            mo().write.assert_called_once_with("a,b\n1,2")

    def test_write_file__csv_rows(self):
        mo = mock_open()
        with patch("builtins.open", mo):
            save.write_file((('a', 'b'), (1, 2)), "directory", "C6L")

            mo().write.assert_any_call("a|b\r\n")
            mo().write.assert_any_call("1|2\r\n")

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
