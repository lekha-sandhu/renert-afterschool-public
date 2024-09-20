# Copyright (C) 2020-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from root import app,db
import pytz

tz = None

def init_globals():
    global tz
    tz =  pytz.timezone("America/Edmonton")

