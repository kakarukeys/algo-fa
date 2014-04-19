import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

from fa.metric import Metric
from fa.inspect import get_first_commonly_available_year
from fa.plot_util import print_point_labels

from settings import archive_directory, symbols, end_date


metrics = [Metric.from_archive(archive_directory, s) for s in symbols]
pe_ratios_list = [m.calc_pe_ratios() for m in metrics]
buy_year = get_first_commonly_available_year(pe_ratios_list)

pe_ratios_at_buy_year_list = [ts.loc[str(buy_year)] for ts in pe_ratios_list]
buy_dates = [ser.index[0] for ser in pe_ratios_at_buy_year_list]
pe_ratios = [ser.iat[0] for ser in pe_ratios_at_buy_year_list]

sell_date = pd.Timestamp(end_date) - np.timedelta64(1, 'D')
percentage_annual_returns = [m.calc_annual_return(buy_date, sell_date) * 100 for m, buy_date in zip(metrics, buy_dates)]

df = pd.DataFrame.from_dict({
	"Symbol": list(symbols.keys()),
	"Name": list(symbols.values()),
	"P/E Ratio": pe_ratios,
	"Annual Return (%)": percentage_annual_returns,
})

title = "Annual Return of stocks bought at {0} sold at {1} over P/E Ratio\n".format(buy_year, sell_date.date())
graph = df.plot(x="P/E Ratio", y="Annual Return (%)", kind="scatter", title=title)

print_point_labels(df, graph, x="P/E Ratio", y="Annual Return (%)", label="Name")

xbound = graph.get_xbound()
graph.hlines(0, *xbound, color="red")

plt.show()
