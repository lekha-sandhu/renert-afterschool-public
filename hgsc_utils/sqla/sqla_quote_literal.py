# Copyright (C) 2020-2023 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

#from: https://stackoverflow.com/a/64632908
def quote_literal(conn,s):
    """
    Quote a string as a literal, according to the current db-engine dialect (e.g. PSQL/MySQL).
    To be used in cases where constructing the SQL as string is needed,
    and sqlalchemy parameters binding can't be used.
    """
    sql_quote_fn = conn.String('').literal_processor(dialect=conn.engine.dialect)
    return sql_quote_fn(value=s)

def quote_sql_literal(s):
    return quote_literal(db,s)
