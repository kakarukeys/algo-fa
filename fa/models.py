import peewee as p


db = p.SqliteDatabase(None) # path to be specified at runtime

class BaseModel(p.Model):
    class Meta:
        database = db

class Stock(BaseModel):
    symbol = p.CharField(unique=True)
    name = p.CharField(null=True)
    industry = p.CharField(null=True)
    sector = p.CharField(null=True)

class MarketIndex(BaseModel):
    symbol = p.CharField(unique=True)
    name = p.CharField(null=True)

# coming:
# class BalanceSheet(BaseModel):
# class IncomeStatement(BaseModel):
# class CashFlow(BaseModel):
# class Price(BaseModel):
