import unittest
from datetime import datetime

import peewee as pw

from fa.database import query
from fa.database.models import *
from tests.util import DBTestCase


class TestQuery(DBTestCase):
    def tearDown(self):
        query.delete_all()

    def test_get_outdated_symbols(self):
        symbols = [
            {"symbol": "C6L.SI", "price_updated_at": None},
            {"symbol": "J7X.SI", "price_updated_at": datetime(2012, 12, 21)},
            {"symbol": "ABC.SI", "price_updated_at": datetime(2013, 1, 1)},
        ]

        with db.transaction():
            Symbol.insert_many(symbols).execute()

        result = list(query.get_outdated_symbols("price", datetime(2013, 1, 1)).dicts())

        self.assertEqual(result, [
            {"symbol": "C6L.SI", "updated_at": None},
            {"symbol": "J7X.SI", "updated_at": datetime(2012, 12, 21)},
        ])

    def test_get_outdated_symbols_category(self):
        symbols = [
            {"symbol": "C6L.SI", "category": "market_index"},
            {"symbol": "J7X.SI", "category": "market_index"},
            {"symbol": "ABC.SI", "category": "stock"},
        ]

        with db.transaction():
            Symbol.insert_many(symbols).execute()

        result = list(query.get_outdated_symbols("price", datetime(2013, 1, 1), "market_index").dicts())

        self.assertEqual(result, [
            {"symbol": "C6L.SI", "updated_at": None},
            {"symbol": "J7X.SI", "updated_at": None},
        ])

    def test_get_record_dates(self):
        symbols = [
            {"symbol": "C6L.SI", "price_updated_at": None},
            {"symbol": "ABC.SI", "price_updated_at": None},
        ]

        balance_sheets = [
            {"symbol_obj": "C6L.SI", "date": datetime(1994, 4, 1), "inventories": 1000},
            {"symbol_obj": "C6L.SI", "date": datetime(1995, 4, 1), "inventories": 2000},
            {"symbol_obj": "ABC.SI", "date": datetime(2000, 4, 1), "inventories": 10000},
        ]

        with db.transaction():
            Symbol.insert_many(symbols).execute()
            BalanceSheet.insert_many(balance_sheets).execute()

        dates = [r.date for r in query.get_record_dates("balance_sheet", "C6L.SI")]
        self.assertEqual(dates, [datetime(1994, 4, 1), datetime(1995, 4, 1)])

    def test_get_fundamentals(self):
        symbols = [
            {"symbol": "C6L.SI"},
            {"symbol": "ABC.SI"},
        ]

        prices = [
            {"symbol_obj": "C6L.SI", "date": datetime(2012, 12, 21), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 7850, "adj_close": 99.9},
            {"symbol_obj": "ABC.SI", "date": datetime(2012, 12, 21), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 4430, "adj_close": 54.4},
            {"symbol_obj": "C6L.SI", "date": datetime(2012, 12, 20), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 6860, "adj_close": 100.4},
            {"symbol_obj": "C6L.SI", "date": datetime(2012, 12, 22), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 3870, "adj_close": 32.6},
        ]

        with db.transaction():
            Symbol.insert_many(symbols).execute()
            Price.insert_many(prices).execute()

        result = list(query.get_fundamentals("price", "C6L.SI", ("date", "volume", "adj_close")).dicts())

        self.assertEqual(result, [
            (datetime(2012, 12, 20), 6860, 100.4),
            (datetime(2012, 12, 21), 7850, 99.9),
            (datetime(2012, 12, 22), 3870, 32.6),
        ])

    def test_update_fundamentals(self):
        symbols = [
            {"symbol": "C6L.SI"},
            {"symbol": "ABC.SI"}
        ]

        balance_sheets = [
            {"symbol_obj": "C6L.SI", "date": datetime(1994, 4, 1), "inventories": 1000},
            {"symbol_obj": "C6L.SI", "date": datetime(1995, 4, 1), "inventories": 2000},
        ]

        with db.transaction():
            Symbol.insert_many(symbols).execute()
            BalanceSheet.insert_many(balance_sheets).execute()

        symbol = "C6L.SI"
        records = [
            {"symbol_obj": "C6L.SI", "date": datetime(1996, 4, 1), "inventories": 4000},
            {"symbol_obj": "C6L.SI", "date": datetime(1997, 4, 1), "inventories": 8000},
        ]
        end_date = datetime(2012, 12, 22)

        query.update_fundamentals("balance_sheet", symbol, records, end_date)

        updated_data = list(BalanceSheet.select(
            BalanceSheet.symbol_obj, BalanceSheet.date, BalanceSheet.inventories
        ).dicts())

        markers = list(Symbol.select(
            Symbol.symbol, Symbol.balance_sheet_updated_at
        ).dicts())

        self.assertEqual(updated_data, balance_sheets + records)
        self.assertEqual(markers, [
            {"symbol": "C6L.SI", "balance_sheet_updated_at": end_date},
            {"symbol": "ABC.SI", "balance_sheet_updated_at": None},
        ])

    def test_update_fundamentals_delete_old(self):
        symbols = [
            {"symbol": "C6L.SI"},
            {"symbol": "ABC.SI"},
        ]

        prices = [
            {"symbol_obj": "C6L.SI", "date": datetime(2012, 12, 21), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 0, "adj_close": 99.9},
            {"symbol_obj": "ABC.SI", "date": datetime(2012, 12, 21), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 0, "adj_close": 669.5},
        ]

        with db.transaction():
            Symbol.insert_many(symbols).execute()
            Price.insert_many(prices).execute()

        symbol = "C6L.SI"
        records = [
            {"symbol_obj": "C6L.SI", "date": datetime(2012, 12, 21), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 0, "adj_close": 100.0},
            {"symbol_obj": "C6L.SI", "date": datetime(2012, 12, 22), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 0, "adj_close": 120.0},
        ]

        query.update_fundamentals("price", symbol, records, datetime(2012, 12, 22), delete_old=True)

        updated_data = list(Price.select().dicts())
        for p in updated_data:
            del p["id"]

        self.assertEqual(updated_data, prices[1:] + records)

    def test_update_fundamentals_exception_handling(self):
        symbols = [
            {"symbol": "C6L.SI"},
        ]

        prices = [
            {"symbol_obj": "C6L.SI", "date": datetime(2012, 12, 21), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 0, "adj_close": 99.9},
        ]

        with db.transaction():
            Symbol.insert_many(symbols).execute()
            Price.insert_many(prices).execute()

        symbol = "C6L.SI"
        records = [ # duplicate events will trigger integrity error
            {"symbol_obj": "C6L.SI", "date": datetime(2012, 12, 22), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 0, "adj_close": 100.0},
            {"symbol_obj": "C6L.SI", "date": datetime(2012, 12, 22), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 0, "adj_close": 120.0},
        ]

        self.assertRaises(pw.IntegrityError, query.update_fundamentals, "price", symbol, records, datetime(2012, 12, 22), delete_old=True)

        # rollback should occur
        updated_data = list(Price.select().dicts())
        for p in updated_data:
            del p["id"]

        markers = list(Symbol.select(
            Symbol.symbol, Symbol.price_updated_at
        ).dicts())

        self.assertEqual(updated_data, prices)
        self.assertEqual(markers, [{"symbol": "C6L.SI", "price_updated_at": None}])

    def test_delete_all(self):
        symbols = [
            {"symbol": "C6L.SI", "price_updated_at": None},
        ]

        prices = [
            {"symbol_obj": "C6L.SI", "date": datetime(2012, 12, 21), "open": 0, "close": 0, "high": 0, "low": 0, "volume": 0, "adj_close": 99.9},
        ]

        with db.transaction():
            Symbol.insert_many(symbols).execute()
            Price.insert_many(prices).execute()

        query.delete_all()

        self.assertEqual(list(Symbol.select()), [])
        self.assertEqual(list(Price.select()), [])

if __name__ == "__main__":
    unittest.main()
