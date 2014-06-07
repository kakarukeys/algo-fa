from fa.archive.load import load_financial_data
from fa.archive.save import dump

from settings import symbols, archive_directory, wsj_archive_directory


""" Enrich financial data with extra data columns calculated from existing columns """

if __name__ == "__main__":
    for s in symbols:
        df = load_financial_data(archive_directory, "income-statement", s)
        insert_index = df.columns.get_loc("Other Operating Expense") + 1
        df.insert(insert_index, "Operating Income", df["Gross Income"] - df["SG&A Expense"] - df["Other Operating Expense"])
        dump({s: df}, wsj_archive_directory, "income-statement")
