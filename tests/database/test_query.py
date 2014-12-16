import unittest

from fa.database import models, query
from tests.util import DBTestCase


class TestQuery(DBTestCase):
    def setUp(self):
        with models.db.transaction():
            models.Stock.insert_many([
                {"symbol": "C6L.SI"},
                {"symbol": "J7X.SI"},
            ]).execute()

    def tearDown(self):
        query.delete_all()

    def test_get_all_symbols(self):
        self.assertEqual(query.get_all_symbols(), ["C6L.SI", "J7X.SI"])

    def test_delete_all(self):
        query.delete_all()
        self.assertEqual(list(models.Stock.select()), [])

if __name__ == "__main__":
    unittest.main()
