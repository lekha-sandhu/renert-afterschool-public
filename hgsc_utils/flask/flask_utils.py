# Copyright (C) 2020-2023 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from flask import session

# See https://stackoverflow.com/a/19525521
def flash_clear_messages():
    session.pop('_flashes', None)
