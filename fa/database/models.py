import peewee as pw

from fa.database import balancesheet_numerical_columns, cashflow_numerical_columns, incomestatement_numerical_columns
from fa.util import  to_pythonic_name


db = pw.SqliteDatabase(None) # path to be specified at runtime

SYMBOL_CATEGORY_CHOICES = (
    ("stock", "Stock"),
    ("market_index", "Market Index"),
)

#------------------------------
# base model to subclass from
#------------------------------

class BaseModel(pw.Model):
    class Meta:
        database = db

#------------------------------
# models for fundamental analytis
#------------------------------

class Symbol(BaseModel):
    symbol = pw.CharField(primary_key=True)
    name = pw.CharField(null=True)
    industry = pw.CharField(null=True)
    sector = pw.CharField(null=True)
    category = pw.CharField(default="stock", choices=SYMBOL_CATEGORY_CHOICES)

    # to keep track of data update
    price_updated_at = pw.DateTimeField(null=True)
    balance_sheet_updated_at = pw.DateTimeField(null=True)
    cash_flow_updated_at = pw.DateTimeField(null=True)
    income_statement_updated_at = pw.DateTimeField(null=True)

class EventModel(pw.Model):
    symbol_obj = pw.ForeignKeyField(Symbol, db_column="symbol", index=True)
    date = pw.DateTimeField()

    # so that symbol lookup will not trigger an extra select query (Peewee's behaviour)
    @property
    def symbol(self):
        return self._data["symbol_obj"]

    class Meta:
        database = db
        indexes = (
            # create a unique composite index
            (("symbol_obj", "date"), True),
        )

class Price(EventModel):
    open = pw.DoubleField()
    high = pw.DoubleField()
    low = pw.DoubleField()
    close = pw.DoubleField()
    volume = pw.BigIntegerField()
    adj_close = pw.DoubleField()

# the 3 financial data models are dynamically generated:

def _get_numerical_column_names(model_name):
    """returns all numerical column names of a financial data model,
       which are converted from verbose names stored in separate files imported.
    """
    verbose_names = globals()[model_name.lower() + "_numerical_columns"].verbose_names
    return [to_pythonic_name(name) for name in verbose_names]

def _create_financial_data_model(model_name):
    column_names = _get_numerical_column_names(model_name)

    return type(
        model_name,
        (EventModel,),
        {name: pw.DoubleField(null=True) for name in column_names}
    )

for model_name in ("BalanceSheet", "CashFlow", "IncomeStatement"):
    globals()[model_name] = _create_financial_data_model(model_name)

#------------------------------------------------
# lists all active models (for iteration purpose)
#------------------------------------------------

export = [Symbol, Price, BalanceSheet, CashFlow, IncomeStatement]
