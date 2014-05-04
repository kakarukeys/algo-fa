import unittest
from unittest.mock import patch, MagicMock

import pandas as pd
import numpy as np

from fa.analysis.finance import Metric, DatedMetric
from fa.archive.load import FINANCIAL_REPORT_TYPES

from tests.util import PandasTestCase


class TestMetric(PandasTestCase):
    def test_from_archive(self):
        with patch("fa.analysis.finance.load_historical_data", MagicMock(return_value='h')) as mock_load_historical_data, \
             patch("fa.analysis.finance.load_financial_data_all", MagicMock(return_value={rt: rt[0] for rt in FINANCIAL_REPORT_TYPES})) as mock_load_financial_data_all, \
             patch("fa.analysis.finance.Metric.__init__", MagicMock(return_value=None)) as mock_constructor:

            obj = Metric.from_archive("/path/to/archive" ,"C6L", 1, b=2)
            mock_load_historical_data.assert_called_once_with("/path/to/archive", "C6L")
            mock_load_financial_data_all.assert_called_once_with("/path/to/archive", "C6L")
            mock_constructor.assert_called_once_with(1, b=2, historical='h', balance_sheet='b', cash_flow='c', income_statement='i')

        self.assertIsInstance(obj, Metric)

    def test_at(self):
        # make up some fake data for testing attribute transfer
        data = lambda: {'d': np.random.randn(3)}
        index = pd.date_range("2012-01-01", periods=3)
        metric = Metric(
            historical=pd.DataFrame(data(), index=index),
            balance_sheet=pd.DataFrame(data(), index=index),
            income_statement=pd.DataFrame(data(), index=index),
            cash_flow=pd.DataFrame(data(), index=index)
        )

        date = pd.Timestamp("2012-12-21")
        obj = metric.at(date)

        self.assertEqual(obj.date, date)
        other_attributes = {k: v for k, v in vars(obj).items() if k != "date"}
        self.assertEqual(other_attributes, vars(metric))
        self.assertIsInstance(obj, DatedMetric)

    def test_calc_return(self):
        historical_data = {"Adj Close": [3.0, 3.5, 4.2], "Close": [3.0, 5.0, 4.2]}
        historical_index = pd.date_range("2012-01-01", periods=3, freq='2D')
        metric = Metric(historical=pd.DataFrame(historical_data, index=historical_index))

        ret1 = metric.calc_return(pd.Timestamp("2012-01-02"), pd.Timestamp("2012-01-04"))
        ret2 = metric.calc_return(pd.Timestamp("2012-01-02"), pd.Timestamp("2012-01-04"), "Close")

        self.assertAlmostEqual(ret1, 0.2)
        self.assertAlmostEqual(ret2, -0.16)

    def test_calc_annual_return(self):
        historical_data = {"Adj Close": [3.0, 3.5, 4.2], "Close": [3.0, 5.0, 4.2]}
        historical_index = pd.date_range("2012-01-01", periods=3, freq='2D')
        metric = Metric(historical=pd.DataFrame(historical_data, index=historical_index))

        annual_return1 = metric.calc_annual_return(pd.Timestamp("2012-01-02"), pd.Timestamp("2012-01-04"))
        annual_return2 = metric.calc_annual_return(pd.Timestamp("2012-01-02"), pd.Timestamp("2012-01-04"), "Close")

        self.assertAlmostEqual(annual_return1, 36.5)
        self.assertAlmostEqual(annual_return2, -29.2)

    def test_calc_pe_ratio(self):
        historical_data = {"Adj Close": [3.0, 3.5, 4.2], "Close": [3.0, 5.0, 4.2]}
        historical_index = pd.to_datetime(["2012-01-01", "2012-01-03", "2012-01-05"])

        income_statement_data = {"EPS (Basic)": [1.2, 2.5, 3.5], "EPS (Diluted)": [6.0, 4.0, 8.0]}
        income_statement_index = pd.to_datetime(["2012-01-01", "2012-01-02", "2012-01-03"])

        metric = Metric(
            historical=pd.DataFrame(historical_data, index=historical_index),
            income_statement=pd.DataFrame(income_statement_data, index=income_statement_index),
            financial_report_preparation_lag=np.timedelta64(1, 'D')
        )

        pe_ratios1 = metric.calc_pe_ratio()
        pe_ratios2 = metric.calc_pe_ratio("Close", "EPS (Diluted)")

        # because of 1 day financial_report_preparation_lag
        expected_index = pd.to_datetime(["2012-01-02", "2012-01-03", "2012-01-04"])
        self.assertFrameEqual(pe_ratios1, pd.Series([2.5, 1.4, 1], index=expected_index))
        self.assertFrameEqual(pe_ratios2, pd.Series([0.5, 1.25, 0.625], index=expected_index))

if __name__ == "__main__":
    unittest.main()
