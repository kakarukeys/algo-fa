from fa.database.models import Stock, export


def get_all_symbols():
    return [s.symbol for s in Stock.select(Stock.symbol)]

def delete_all():
    for Model in export:
        Model.delete().execute()
