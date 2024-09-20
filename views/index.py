# Copyright (C) 2020-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from pprint import pprint,pformat
from sqlalchemy import text
import sqlalchemy.exc
import json
from  sqlalchemy.sql.expression import func

from flask import request, render_template, redirect, url_for, abort, session
from flask import flash, current_app

from root import app,db

from models.students import Student
import global_settings


@app.route('/')
def index():
    # Get name of a random staf member
    s = Student.query.filter_by(grade='Staff').order_by(func.random()).first()
    pprint(s)
    return render_template("index.html",
                           random_person=s)
