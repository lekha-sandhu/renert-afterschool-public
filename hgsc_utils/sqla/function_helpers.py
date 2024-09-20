# Copyright (C) 2023-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from sqlalchemy import text
from root import db

def psql_get_functions(funcname=None):
    """
    Returns a list of PostgreSQL funtions,
    and their parameters (in-case of function overloading).

    if 'funcname' is not None, return only functions matching that name.
    """
    sql_where_clause = "(1=1)"
    if funcname:
        sql_where_clause = "( lower(routine_name) = lower(:funcname) )"

    sql = """
    with
      src as (
         SELECT
           routines.specific_name,
           routines.routine_name,

           -- convert to 'text' so that SQLAlchemy can automatically convert array_agg to python list.
           -- it doesn't do it automatically for non-standard types.
           parameters.data_type\:\:text,

           parameters.ordinal_position,
           parameters.is_result
       FROM
        information_schema.routines
     LEFT JOIN
        information_schema.parameters
      ON
        routines.specific_name=parameters.specific_name
      WHERE
         routines.specific_schema='public'
       and
         """ + sql_where_clause + """
   )

   select
     specific_name,
     max(routine_name) as routine_name,
     array_agg(data_type order by ordinal_position) FILTER (where data_type is not null) as parameters
   from
     src
   group by
     specific_name
  ORDER BY
     max(routine_name);
    """

    rc = db.session.execute(text(sql), {"funcname": funcname} )
    rc = [x._asdict() for x in rc]
    return rc

def psql_function_exists(funcname):
    """
    Returns TRUE if a postgresql function exists.

    FIXME: This DOES NOT take function-overloading into account.
    """

    rc = psql_get_functions(funcname)
    return len(rc)>0
