import numpy as np
import pandas as pd

from fa.analysis.io import load_fundamental_data

import initialize


initialize.init()

# average annual dividends per $ share price
# figure comes from http://www.spdrs.com.sg/etf/fund/fund_detail_STTF.html
DISTRIBUTION_YIELD = 0.0272

def get_valuation(return_in_one_year):
    if return_in_one_year < 0.10:
        return "O"  # over-valued
    else:
        return "U"  # under-valued

def calc_future_return(price, no_of_days):
    """ returns the return after <no_of_days> days
        if one bought at respective prices at respective dates in <price>
    """
    # if the stock market is not open on the sell day,
    # sell the stock on the morning of the next available day.
    future_price = price.asfreq('1D', method='pad')
    future_price.index = future_price.index - pd.offsets.Day(no_of_days)
    return (future_price / price).dropna() - 1

def get_hold_period(sell_date, dataset):
    buy_date = pd.Series(dataset.index, index=dataset.index)
    return sell_date - buy_date

def study_strategy(amount_invested, dataset, sell_date, sell_price):
    total_amount_invested = amount_invested.sum()
    print("total dollar invested = {0}".format(total_amount_invested))

    units_bought = amount_invested / dataset["Close"]
    total_units_bought = units_bought.sum()
    print("total units bought = {0:.4f}".format(total_units_bought))

    cash_flow_period = (dataset.index[-1] - dataset.index[0]).days / 365
    print("period investing money = {0:.1f} years".format(cash_flow_period))
    print("sell the investment one year after the period,")

    # not reinvesting the dividends
    hold_period_years = get_hold_period(sell_date, dataset) / np.timedelta64(365, 'D')
    dividend_payout = amount_invested * hold_period_years * DISTRIBUTION_YIELD
    total_dividend_payout = dividend_payout.sum()
    print("estimated total dividend payout = {0:.0f}".format(total_dividend_payout))

    capital_gain = total_units_bought * sell_price - total_amount_invested
    print("capital gain = {0:.0f}".format(capital_gain))

    total_gain = capital_gain + total_dividend_payout
    total_return = total_gain / total_amount_invested
    print("total return = {0:.0f}% after {1:.1f} years.".format(total_return * 100, cash_flow_period + 1))

    dividend_payout_proportion = total_dividend_payout / total_gain
    print("dividend payout comprises {0:.0f}%".format(dividend_payout_proportion * 100))

    all_return = ((units_bought * sell_price + dividend_payout) / amount_invested - 1).replace(np.inf, np.nan)
    annual_return = all_return / hold_period_years
    print("average annual return = {0:.1f}%".format(annual_return.mean() * 100))

if __name__ == "__main__":
    symbol = "^STI"

    historical_data = load_fundamental_data("price", symbol)
    price = historical_data["Close"]

    return_in_1yr = calc_future_return(price, 365)
    valuation = return_in_1yr.map(get_valuation)
    valuation.index.name = "Date"
    valuation.name = "Valuation"

    # main working dataset for the study
    dataset = pd.concat([price, valuation], axis=1).dropna()

    # with open("output.csv", 'w') as f:
    #     dataset.to_csv(f)

    # one year after the last investment
    sell_date = price.index[-1]
    sell_price = price[-1]

    print("Studying Dollar Cost Averaging strategy")
    amount_invested_dca = dataset.apply(lambda r: 1, axis=1)
    amount_invested_dca.name = "Invest"
    study_strategy(amount_invested_dca, dataset, sell_date, sell_price)

    print()

    print("Studying God strategy")
    # God is always able to predict stock market downturn correctly and invest at the right time
    amount_invested_god = (dataset["Valuation"] == "U").map(np.int)
    amount_invested_god.name = "Invest"
    study_strategy(amount_invested_god, dataset, sell_date, sell_price)
