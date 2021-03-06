import unittest
from unittest.mock import patch, MagicMock, call
from datetime import datetime

import peewee as pw

from fa.database import models
from tests.util import DBTestCase


class TestModels(DBTestCase):
    def test_whether_models_use_database(self):
        for Model in models.export:
            self.assertIs(Model._meta.database, models.db)

    def test_models(self):
        symbol = "C6L.SI"
        dt = datetime(2012, 12, 21)

        try:
            models.Symbol.create(symbol=symbol, price_updated_at=dt)
            models.Price.create(symbol_obj=symbol, date=dt, open=1.0, close=1.0, high=1.0, low=1.0, volume=10, adj_close=1.0)
            models.BalanceSheet.create(symbol_obj=symbol, date=dt, cash_only=123.45)
            models.CashFlow.create(symbol_obj=symbol, date=dt, free_cash_flow=456.78)
            models.IncomeStatement.create(symbol_obj=symbol, date=dt, ebit_margin=901.23)

            for Model in models.export:
                self.assertEqual(Model.get().symbol, "C6L.SI")

            self.assertEqual(models.BalanceSheet.get().cash_only, 123.45)
            self.assertEqual(models.CashFlow.get().free_cash_flow, 456.78)
            self.assertEqual(models.IncomeStatement.get().ebit_margin, 901.23)

        except (pw.DatabaseError, NameError):
            self.fail("models not declared properly!")

    def test_get_numerical_column_names(self):
        with patch("fa.database.balancesheet_numerical_columns.verbose_names", ["abc", "def"]):
            names = models.get_numerical_column_names("BalanceSheet")
        self.assertEqual(names, ["abc", "def"])

    def test_numerical_column_names_uniqueness(self):
        for model_name in ("BalanceSheet", "CashFlow", "IncomeStatement"):
            names = models.get_numerical_column_names(model_name)
            self.assertTrue(
                len(names) == len(set(names)),
                "two verbose column names in {0} are mapped to the same pythonic name!".format(model_name)
            )

    def test_get_Model(self):
        self.assertEqual(models.get_Model("balance_sheet"), models.BalanceSheet)

if __name__ == "__main__":
    unittest.main()
