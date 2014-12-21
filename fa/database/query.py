from fa.database.models import Symbol, export


def get_symbols_to_update_data(end_date):
    """ Gets symbols which data is never updated or was updated before <end_date>
        end_date: datetime object
    """
    return [s.symbol for s in Symbol.select(Symbol.symbol).where(
        (Symbol.price_updated_at < end_date) | (Symbol.price_updated_at == None)
    )]

def delete_all():
    for Model in export:
        Model.delete().execute()
