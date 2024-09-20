# Copyright (C) 2020-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from root import db, app
from sqlalchemy import text

def set_db_default_timezone(tz):
    sql = """SET TIME ZONE :tz"""
    db.session.execute( text(sql), { "tz" : tz } )
