from functools import reduce

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from fa.analysis.finance import Metric, PROFIT_MARGIN_KINDS
from fa.analysis.measurement import get_first_commonly_available_year

from plot_util import print_point_labels
from settings import archive_directory, symbols, end_date


metrics = [Metric.from_archive(archive_directory, s) for s in symbols]
pe_ratios_list = [m.calc_pe_ratio() for m in metrics]

# figure 1
fig = plt.figure(figsize=(12, 10))

title = "P/E Ratio of stocks over Date\n"
xticks = reduce(lambda a, b: a | b, [ts.index for ts in pe_ratios_list])

with pd.plot_params.use('x_compat', True):
    for series, label in zip(pe_ratios_list, symbols.values()):
        graph = series.plot(label=label, legend=True, title=title, xticks=xticks)
        graph.set_xlabel("Date")
        graph.set_ylabel("P/E Ratio")

# prepare graph data
buy_year = get_first_commonly_available_year(pe_ratios_list)
pe_ratios_at_buy_year_list = [ts.loc[str(buy_year)] for ts in pe_ratios_list]
buy_dates = [ser.index[0] for ser in pe_ratios_at_buy_year_list]
pe_ratios = [ser.iat[0] for ser in pe_ratios_at_buy_year_list]

dated_metrics = [m.at(buy_date) for m, buy_date in zip(metrics, buy_dates)]

sell_date = pd.Timestamp(end_date) - np.timedelta64(1, 'D')
percentage_annual_returns = [dm.calc_annual_return(sell_date) * 100 for dm in dated_metrics]

profit_margin_labels = [k.title() + " Profit Margin (%)" for k in PROFIT_MARGIN_KINDS]
profit_margins = {
    label: [dm.calc_profit_margin(kind) * 100 for dm in dated_metrics]
    for label, kind in zip(profit_margin_labels, PROFIT_MARGIN_KINDS)
}

graph_data = {
    "Symbol": list(symbols.keys()),
    "Name": list(symbols.values()),
    "P/E Ratio": pe_ratios,
    "Annual Return (%)": percentage_annual_returns,
}
graph_data.update(profit_margins)

df = pd.DataFrame.from_dict(graph_data)

# figure 2
title = "Annual Return of stocks bought in {0} sold at {1} over P/E Ratio\n".format(buy_year, sell_date.date())
graph = df.plot(x="P/E Ratio", y="Annual Return (%)", kind="scatter", title=title, figsize=(12, 10))
print_point_labels(df, graph, x="P/E Ratio", y="Annual Return (%)", label="Name")

xbound = graph.get_xbound()
graph.hlines(0, *xbound, color="red")

# figure 3
title = "Gross Profit Margin of stocks in {0} over P/E Ratio\n".format(buy_year)
graph = df.plot(x="P/E Ratio", y="Gross Profit Margin (%)", kind="scatter", title=title, figsize=(12, 10))
print_point_labels(df, graph, x="P/E Ratio", y="Gross Profit Margin (%)", label="Name")

# figure 4
new_df = df[profit_margin_labels + ["Name"]].set_index("Name").transpose()
title = "Profit Margins of stocks in {0}".format(buy_year)
new_df.plot(subplots=True, kind="bar", rot=20, title=title, figsize=(8, 13))

# show all figures
plt.show()
