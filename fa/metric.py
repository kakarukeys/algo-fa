import numpy as np
from .calculator import translate_index
from .loader import load_historical_data, load_financial_data_all


class Metric(object):
	def __init__(self,
			historical,
			balance_sheet,
			income_statement,
			cash_flow,
			financial_report_preparation_lag=np.timedelta64(30, 'D')
		):
		""" Returns an object that is capable of calculating various metrics of the stock.
			historical, balance_sheet, income_statement, cash_flow: respective DataFrame objects
			financial_report_preparation_lag (np.timedelta64 object):
				how long does it take to release the financial report after the end of fiscal year?
				default: 30 days.
		"""
		self.historical = historical
		self.balance_sheet = balance_sheet
		self.income_statement = income_statement
		self.cash_flow = cash_flow
		self.financial_report_preparation_lag = financial_report_preparation_lag

		# historical data with missing dates filled in, with values from future
		self.historical_fillforward = historical.resample('1D', fill_method="ffill")

		# historical data with missing dates filled in, with values from past
		self.historical_fillbackward = historical.resample('1D', fill_method="bfill")

		# financial reports with the lag in information release factored in
		self.balance_sheet_lagged = translate_index(balance_sheet, self.financial_report_preparation_lag)
		self.income_statement_lagged = translate_index(income_statement, self.financial_report_preparation_lag)
		self.cash_flow_lagged = translate_index(cash_flow, self.financial_report_preparation_lag)

	@classmethod
	def from_archive(cls, archive_directory, symbol, **kwargs):
		""" Returns an object that is capable of calculating various metrics of the stock.
			archive_directory: will load data from this directory to construct the object
			symbol: e.g. "C6L"
			Any extra keyword arguments will be passed to the constructor.
		"""
		historical_data = load_historical_data(archive_directory, symbol)
		financial_data = load_financial_data_all(archive_directory, symbol)

		return cls(
			historical_data,
			financial_data["balance-sheet"],
			financial_data["income-statement"],
			financial_data["cash-flow"],
			**kwargs
		)

	def calc_return(self, buy_date, sell_date, price_column="Adj Close"):
		""" Returns the return of the stock if a buy market order is made on <buy_date> and a sell market order is
			made on <sell_date>.
			buy_date, sell_date: pd.Timestamp object
			price_column: the column to get prices, default: "Adj Close".
		"""
		# use fillbackward here because a market order is executed as soon as a price is available
		buy_price = self.historical_fillbackward.at[buy_date, price_column]
		sell_price = self.historical_fillbackward.at[sell_date, price_column]
		return sell_price / buy_price - 1

	def calc_annual_return(self, buy_date, sell_date, price_column="Adj Close"):
		""" Returns the annualized return of the stock if a buy market order is made on <buy_date> and a sell market order is
			made on <sell_date>.
			buy_date, sell_date: pd.Timestamp object
			price_column: the column to get prices, default: "Adj Close".
		"""
		ret = self.calc_return(buy_date, sell_date, price_column)
		conversion_factor = np.timedelta64(365, 'D') / (np.datetime64(sell_date) - np.datetime64(buy_date))
		return ret * conversion_factor

	def calc_pe_ratios(self, price_column="Adj Close", eps_column="EPS (Basic)"):
		""" Returns the P/E Ratio of the stock at dates where the ratio is computable.
			price_column: the column to get prices, default: "Adj Close".
			eps_columm: the column to get EPS, default: "EPS (Basic)"
		"""
		eps = self.income_statement_lagged[eps_column]
		pps = self.historical_fillforward.loc[eps.index, price_column]	# use fillforward here to avoid peeking into future
		return pps / eps
