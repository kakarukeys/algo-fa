import unittest
from datetime import datetime

import peewee as pw

from fa.database import query
from fa.database.models import *
from tests.util import DBTestCase


class TestQuery(DBTestCase):
    def setUp(self):
        self.symbols = [
            {"symbol": "C6L.SI", "price_updated_at": None},
            {"symbol": "J7X.SI", "price_updated_at": datetime(2012, 12, 21)},
            {"symbol": "ABC.SI", "price_updated_at": datetime(2013, 1, 1)},
        ]

        self.prices = [
            {"symbol_obj": "C6L.SI", "date": datetime(2012, 12, 21), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 0, "adj_close": 99.9},
        ]

        with db.transaction():
            Symbol.insert_many(self.symbols).execute()
            Price.insert_many(self.prices).execute()

    def tearDown(self):
        query.delete_all()

    def test_get_outdated_symbols(self):
        symbols = query.get_outdated_symbols("price", datetime(2013, 1, 1))
        self.assertEqual(symbols, ["C6L.SI", "J7X.SI"])

    def test_update_historical_prices(self):
        symbol = "C6L.SI"
        records = [
            {"symbol_obj": "C6L.SI", "date": datetime(2012, 12, 21), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 0, "adj_close": 100.0},
            {"symbol_obj": "C6L.SI", "date": datetime(2012, 12, 22), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 0, "adj_close": 120.0},
        ]
        end_date = datetime(2012, 12, 22)

        query.update_historical_prices(symbol, records, end_date)

        updated_prices = list(Price.select().where(Price.symbol_obj == symbol).dicts())
        for p in updated_prices:
            del p["id"]

        marker = Symbol.select(Symbol.price_updated_at).where(Symbol.symbol == symbol).get().price_updated_at

        self.assertEqual(updated_prices, records)
        self.assertEqual(marker, end_date)

    def test_update_historical_prices_exception_handling(self):
        symbol = "C6L.SI"
        records = [ # duplicate events will trigger integrity error
            {"symbol_obj": "C6L.SI", "date": datetime(2012, 12, 22), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 0, "adj_close": 100.0},
            {"symbol_obj": "C6L.SI", "date": datetime(2012, 12, 22), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 0, "adj_close": 120.0},
        ]
        end_date = datetime(2012, 12, 22)

        self.assertRaises(pw.IntegrityError, query.update_historical_prices, symbol, records, end_date)

        # rollback should occur
        updated_prices = list(Price.select().where(Price.symbol_obj == symbol).dicts())
        for p in updated_prices:
            del p["id"]

        marker = Symbol.select(Symbol.price_updated_at).where(Symbol.symbol == symbol).get().price_updated_at

        self.assertEqual(updated_prices, self.prices)
        self.assertIs(marker, None)

    def test_delete_all(self):
        query.delete_all()
        self.assertEqual(list(Symbol.select()), [])

if __name__ == "__main__":
    unittest.main()
