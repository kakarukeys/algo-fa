import pandas as pd

from fa.database.models import get_numerical_column_names
from fa.database.query import get_fundamentals
from fa.util import to_pythonic_name


def load_fundamental_data(data_type, symbol, columns=None):
    """ Returns a DataFrame object containing <data_type> fundamental data of <symbol> with <columns>.

        data_type: name of *_updated_at fields in Symbol model without _updated_at
        symbol: e.g. 'C6L.SI'
        columns: a sequence of column names as defined in fa.database.*_numerical_columns modules.
            Default: None - include all.
    """
    if columns is None:
        model_name = data_type.replace('_', '')
        columns = get_numerical_column_names(model_name)

    columns = ["Date"] + list(columns)

    field_names = [to_pythonic_name(c) for c in columns]
    records = get_fundamentals(data_type, symbol, field_names)

    return pd.DataFrame.from_records(records, columns=columns, index="Date")
