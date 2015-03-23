from fa.database.models import IncomeStatement
import initialize


""" Enrich financial data with extra data columns calculated from existing columns """

initialize.init()

IncomeStatement \
    .update(operating_income=(
        IncomeStatement.gross_income -
        IncomeStatement.sg_a_expense -
        IncomeStatement.other_operating_expense
    )) \
    .where(IncomeStatement.operating_income >> None) \
    .execute()
