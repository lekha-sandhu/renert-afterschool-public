# Copyright (C) 2020-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from pprint import pprint,pformat
from sqlalchemy import text
import sqlalchemy.exc
import json

from flask import request, render_template, redirect, url_for, abort, session
from flask import flash, current_app

from root import app,db

import global_settings


@app.route('/')
def index():
    return render_template("index.html")
