import unittest
from datetime import datetime

from fa.database import models, query
from tests.util import DBTestCase


class TestQuery(DBTestCase):
    def setUp(self):
        with models.db.transaction():
            models.Symbol.insert_many([
                {"symbol": "C6L.SI", "price_updated_at": None},
                {"symbol": "J7X.SI", "price_updated_at": datetime(2012, 12, 21)},
                {"symbol": "ABC.SI", "price_updated_at": datetime(2013, 1, 1)},
            ]).execute()

    def tearDown(self):
        query.delete_all()

    def test_get_symbols_to_update_data(self):
        symbols = query.get_symbols_to_update_data(datetime(2013, 1, 1))
        self.assertEqual(symbols, ["C6L.SI", "J7X.SI"])

    def test_delete_all(self):
        query.delete_all()
        self.assertEqual(list(models.Symbol.select()), [])

if __name__ == "__main__":
    unittest.main()
