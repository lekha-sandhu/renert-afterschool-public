# Copyright (C) 2020-2023 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

from pprint import pformat, pprint
from random import randint
import traceback
from flask import abort, request
from werkzeug.exceptions import InternalServerError
from sqlalchemy.exc import SQLAlchemyError
from datetime import datetime

from root import app,db
from models.exceptions_log import ExceptionLog

import global_settings

def setup_exception_handler(app_name):

    exception_file = open("exceptions.log","ab+",buffering=0)

    #from https://flask.palletsprojects.com/en/1.1.x/errorhandling/#unhandled-exceptions
    #This requires Flask>=1.1.0 to work, otherwise "original_exception" will be None.

    @app.errorhandler(InternalServerError)
    def handle_500(e):
        marker = randint(100000,999999)

        original = getattr(e, "original_exception", None)

        tmp = original if original else e

        exception_class = type(tmp).__name__
        exception_desc = str(tmp)
        tmp_tb = traceback.extract_tb(tmp.__traceback__)
        exception_data = ''.join(traceback.format_list(tmp_tb))

        # Try to get the filename/line-number
        exception_filename = None
        exception_lineno = None
        if len(tmp_tb):
            tmp_frame = tmp_tb[-1]
            exception_filename = tmp_frame.filename
            exception_lineno = tmp_frame.lineno

        local_time = datetime.now(tz=global_settings.tz)
        utc_time = datetime.utcnow()

        text_msg="""
EXCEPTION:
MARKER: {marker}
APP: {app_name}
LOCAL_TIME: {local_time}
UTC_TIME: {utc_time}
HTTP_REMOTE_ADDR: {remote_addr}
HTTP_URL: {url}
HTTP_USER_AGENT: {user_agent}
HTTP_REFERRER: {referrer}
DEV_MODE: {dev_mode}
EXCEPTION_CLASS: {exception_class}
EXCEPTION_DESCRIPTION: {exception_desc}
EXCEPTION_FILENAME: {exception_filename}
EXCEPTION_LINENO: {exception_lineno}
EXCEPTION_TRACEBACK: {exception_traceback}

        """.format(app_name=app_name, marker=marker,
                   local_time=local_time, utc_time=utc_time,
                   remote_addr = request.remote_addr,
                   url = request.url,
                   user_agent = request.user_agent.string,
                   referrer = request.referrer,
                   exception_filename = exception_filename,
                   exception_lineno = exception_lineno,
                   exception_class = exception_class,
                   exception_desc = exception_desc,
                   exception_traceback = exception_data,
                   dev_mode = app.debug)

        ## Easiest: print to STDOUT
        print(text_msg)

        ## Next: write to a text file
        try:
            exception_file.write(text_msg.encode())
            exception_file.flush()
        except (OSError,OSError):
            print("ERROR: failed to write exception data to exception file (marker %d)" % marker)
            pass


        ## Most complicated/risky - add record to database
        try:
            el = ExceptionLog()

            el.app_name = app_name
            el.marker = marker
            el.exception_class = exception_class
            el.exception_description = exception_desc
            el.exception_traceback = exception_data
            el.exception_filename = exception_filename
            el.exception_lineno = exception_lineno


            # HTTP/Client data
            el.url = request.url
            el.remote_addr = request.remote_addr
            el.user_agent = request.user_agent.string
            el.referrer = request.referrer

            el.dev_mode = app.debug

            db.session.add(el)
            db.session.commit()
        except SQLAlchemyError:
            print("ERROR: Failed to add exception data to database (marker %d)" % marker)
            pass


        if original is None:
            # direct 500 error, such as abort(500)
            return "Internal Server Error: Aborted (code %d)" % (marker), 500 # render_template("500.html"), 500

        # wrapped unhandled error
        return "Interal Server Error: Unhandled Exception (code %d)" % (marker) ###render_template("500_unhandled.html", e=original), 500


    @app.route('/raise')
    def raise_exception():
        # This will raise an exception
        foo = open("/no/such/file","r")

    @app.route('/raise2')
    def raise_exception2():
        # This should raise an exception
        abort(500)

    @app.route('/raise3')
    def raise_exception3():
        # This should raise an exception
        return "I can't do that, Dave", 500
