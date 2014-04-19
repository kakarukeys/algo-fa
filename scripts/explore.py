import matplotlib.pyplot as plt

from settings import archive_directory, symbols
from fa.loader import load_historical_data, load_financial_data_all
from fa.metric import Metric


s = "C6L"
historical_data = load_historical_data(archive_directory, s)
financial_data = load_financial_data_all(archive_directory, s)

metric = Metric(
	historical_data,
	financial_data["balance-sheet"],
	financial_data["income-statement"],
	financial_data["cash-flow"]
)
pe_ratios = metric.calc_pe_ratios()
print(pe_ratios)

plt.figure()

graph = pe_ratios.plot(label=symbols[s])
graph.set_xlabel("Period")
graph.set_ylabel("P/E Ratio")
graph.set_title("P/E Ratio of SIA over different periods")

plt.legend()
plt.show()
