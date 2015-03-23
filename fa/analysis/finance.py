import numpy as np
from fa.calculator import translate_index
from fa.analysis.io import load_fundamental_data


PROFIT_MARGIN_KINDS = ("gross", "operating", "pretax", "net")

class Metric(object):
    def __init__(self,
            historical=None,
            balance_sheet=None,
            income_statement=None,
            cash_flow=None,
            financial_report_preparation_lag=np.timedelta64(30, 'D')
        ):
        """ Returns an object that is capable of calculating various metrics of the stock.
            historical, balance_sheet, income_statement, cash_flow: respective DataFrame objects, default: None
            financial_report_preparation_lag (np.timedelta64 object):
                how long does it take to release the financial report after the end of fiscal year?
                default: 30 days.
        """
        self.historical = historical
        self.balance_sheet = balance_sheet
        self.income_statement = income_statement
        self.cash_flow = cash_flow
        self.financial_report_preparation_lag = financial_report_preparation_lag

        if historical is not None:
            # historical data with missing dates filled in, with values from future
            self.historical_fillforward = historical.resample('1D', fill_method="ffill")

            # historical data with missing dates filled in, with values from past
            self.historical_fillbackward = historical.resample('1D', fill_method="bfill")

        # financial reports with the lag in information release factored in
        if balance_sheet is not None:
            self.balance_sheet_lagged = translate_index(balance_sheet, self.financial_report_preparation_lag)

        if income_statement is not None:
            self.income_statement_lagged = translate_index(income_statement, self.financial_report_preparation_lag)

        if cash_flow is not None:
            self.cash_flow_lagged = translate_index(cash_flow, self.financial_report_preparation_lag)

    @classmethod
    def from_archive(cls, symbol, *args, **kwargs):
        """ Returns an object that is capable of calculating various metrics of the stock,
            with data loaded from archive.

            symbol: e.g. "C6L.SI"
            Any extra arguments will be passed on to the constructor.
        """
        kwargs.update({
            "historical": load_fundamental_data("price", symbol),
            "balance_sheet": load_fundamental_data("balance_sheet", symbol),
            "income_statement": load_fundamental_data("income_statement", symbol),
            "cash_flow": load_fundamental_data("cash_flow", symbol),
        })

        return cls(*args, **kwargs)

    def at(self, date):
        """ Fixes the internal date to <date> (pd.Timestamp object) to be used for calculation of metrics. """
        dm = DatedMetric(date)
        dm.__dict__.update(self.__dict__)   # bring over all attributes
        return dm

    def _calc_return(self, buy_date, sell_date, price_column):
        # use fillbackward here because a market order is executed as soon as a price is available
        buy_price = self.historical_fillbackward.at[buy_date, price_column]
        sell_price = self.historical_fillbackward.at[sell_date, price_column]
        return sell_price / buy_price - 1

    def calc_return(self, buy_date, sell_date, price_column="Adj Close"):
        """ Returns the return of the stock if a buy market order is made on <buy_date> and a sell market order is
            made on <sell_date>.
            buy_date, sell_date: pd.Timestamp object
            price_column: the column to get prices, default: "Adj Close".
        """
        return self._calc_return(buy_date, sell_date, price_column)

    def calc_annual_return(self, buy_date, sell_date, price_column="Adj Close"):
        """ Returns the annualized return of the stock if a buy market order is made on <buy_date> and a sell market order is
            made on <sell_date>.
            buy_date, sell_date: pd.Timestamp object
            price_column: the column to get prices, default: "Adj Close".
        """
        ret = self._calc_return(buy_date, sell_date, price_column)
        conversion_factor = np.timedelta64(365, 'D') / (np.datetime64(sell_date) - np.datetime64(buy_date))
        return ret * conversion_factor

    def calc_pe_ratio(self, price_column="Adj Close", eps_column="EPS (Basic)"):
        """ Returns the P/E Ratio series of the stock.
            price_column: the column to get prices, default: "Adj Close".
            eps_columm: the column to get EPS, default: "EPS (Basic)"
        """
        eps = self.income_statement_lagged[eps_column]
        pps = self.historical_fillforward.loc[eps.index, price_column]  # use fillforward here to avoid peeking into future
        return pps / eps

    def calc_profit_margin(self, kind):
        """ Returns the Profit Margin series of the stock.
            kind: a string in PROFIT_MARGIN_KINDS
        """
        profit = self.income_statement_lagged[kind.title() + " Income"]
        revenue = self.income_statement_lagged["Sales/Revenue"]

        return profit / revenue

class DatedMetric(Metric):
    def __init__(self, date, **kwargs):
        """ Returns an object that is capable of calculating various metrics of the stock at <date>.
            Takes arguments of Metric constructor as extra keyword arguments.
        """
        super(DatedMetric, self).__init__(**kwargs)
        self.date = date

    def calc_return(self, *args, **kwargs):
        """ Returns the return of the stock if a buy market order is made on the internal date and a sell market order is
            made on <sell_date>.
            sell_date: pd.Timestamp object
            price_column: the column to get prices, default: "Adj Close".
        """
        return super(DatedMetric, self).calc_return(self.date, *args, **kwargs)

    def calc_annual_return(self, *args, **kwargs):
        """ Returns the annualized return of the stock if a buy market order is made on the internal date and a sell market order is made on <sell_date>.
            sell_date: pd.Timestamp object
            price_column: the column to get prices, default: "Adj Close".
        """
        return super(DatedMetric, self).calc_annual_return(self.date, *args, **kwargs)

    def calc_pe_ratio(self, price_column="Adj Close", eps_column="EPS (Basic)"):
        """ Returns the P/E Ratio of the stock at the internal date.
            price_column: the column to get prices, default: "Adj Close".
            eps_columm: the column to get EPS, default: "EPS (Basic)"
        """
        eps = self.income_statement_lagged.at[self.date, eps_column]
        pps = self.historical_fillforward.at[self.date, price_column]
        return pps / eps

    def calc_profit_margin(self, kind):
        """ Returns the Profit Margin of the stock at the internal date.
            kind: a string in PROFIT_MARGIN_KINDS
        """
        profit = self.income_statement_lagged.at[self.date, kind.title() + " Income"]
        revenue = self.income_statement_lagged.at[self.date, "Sales/Revenue"]

        return profit / revenue
