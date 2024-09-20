# Copyright (C) 2020-2023 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from sqlalchemy import Index
from datetime import datetime
from flask import request
from root import db

class ExceptionLog(db.Model):
    __tablename__ = 'exceptions_log'

    exception_log_id = db.Column(db.Integer, primary_key=True)

    """ Data Fields """
    ts = db.Column(db.TIMESTAMP(timezone=True),index=True,default=datetime.utcnow)

    # Server/Exception Data
    app_name = db.Column(db.String,index=True)
    marker = db.Column(db.Integer)
    exception_class = db.Column(db.String)
    exception_description = db.Column(db.String)
    exception_traceback = db.Column(db.Text)
    exception_filename = db.Column(db.String)
    exception_lineno = db.Column(db.Integer)


    # HTTP/Client data
    url = db.Column(db.String)
    remote_addr = db.Column(db.String)
    user_agent = db.Column(db.String)
    referrer = db.Column(db.String)


    # Troubleshooting helper data
    insepected = db.Column(db.Boolean,index=True)
    comments = db.Column(db.String)

    dev_mode = db.Column(db.Boolean,default=False,index=True)
