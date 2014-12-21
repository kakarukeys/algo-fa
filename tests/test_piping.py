import unittest

from fa import piping


class TestPiping(unittest.TestCase):
    def test_csv_string_to_records(self):
        records = piping.csv_string_to_records(
            "C6L.SI",
            "Operating Income & Loss,Revenue\n100.0,200.0\n300.0,400.0\n"
        )

        self.assertEqual(list(records), [
            {"symbol_obj": "C6L.SI", "operating_income_loss": "100.0", "revenue": "200.0"},
            {"symbol_obj": "C6L.SI", "operating_income_loss": "300.0", "revenue": "400.0"},
        ])

    def test_csv_string_to_records_delimiter(self):
        records = piping.csv_string_to_records(
            "C6L.SI",
            "Operating Income & Loss|Revenue\n100.0|200.0\n300.0|400.0\n",
            delimiter='|'
        )

        self.assertEqual(list(records), [
            {"symbol_obj": "C6L.SI", "operating_income_loss": "100.0", "revenue": "200.0"},
            {"symbol_obj": "C6L.SI", "operating_income_loss": "300.0", "revenue": "400.0"},
        ])

if __name__ == "__main__":
    unittest.main()
