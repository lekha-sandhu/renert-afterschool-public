# Copyright (C) 2020-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

# Load the main flask APP object, and set config variables
# before anything else (e.g. before initializing DB) -
# this way everything else has access to "app.config[]" settings.
from root import app,db,csrf,admin
app.config.from_envvar('CONFIG_FILE')


# Fix Working behind NGIXN proxy.
# This ensures that flask's "request.remote_addr" will be the address
# of the client, not of the 127.0.0.1 of the NGINX front-end.
from werkzeug.middleware.proxy_fix import ProxyFix
app.wsgi_app = ProxyFix(app.wsgi_app)


"""
# Server-side sessions
from flask_session import Session
Session(app)
"""

import global_settings

# Enable the Flask Debug Toolbar (FDT) - a debug toolbar
# will appear on each rendered HTML page, exposing flask config variables
# and other useful data.
from flask_debugtoolbar import DebugToolbarExtension
if app.debug:
    # We rarely want this option turned on.
    app.config["DEBUG_TB_INTERCEPT_REDIRECTS"] = False
    #toolbar = DebugToolbarExtension(app)

# Setup Database, create all tables if needed.
db.app = app
db.init_app(app)

# Load Database model classes
import models
from models.exceptions_log import ExceptionLog
from models.students import Student
from models.afterschool_classes import AfterschoolClass
from models.afterschool_signins import AfterschoolSignin
from models.members import Member
from models.login_users import LoginUser
from models.permissions import Permission,Role,RoleToPermission,LoginUserToRole,permission_required

with app.app_context():
    db.create_all()
    db.session.commit()

global_settings.init_globals()

from hgsc_utils.flask.gunicorn_logging_hack import test_logging_messages,set_logger_level_info_or_debug
from hgsc_utils.flask.logtest_blueprint import logtest_blueprint
import hgsc_utils.flask.flask_util_nocache

set_logger_level_info_or_debug(app)
test_logging_messages(app)
app.register_blueprint(logtest_blueprint, url_prefix="/logtest")

# Initialize Flask-User LoginManager
from flask_login import LoginManager

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(login_user_id):
    #app.logger.debug("load-user: login_user_id = %d" % login_user_id)
    user = LoginUser.query.get(login_user_id)
    #app.logger.debug("load-user: loaded user %s" % (str(user)))
    return user


# Load custom Jinja2 filters
import jinja_filters

# Load Generic Exception Handler
from exception_handler import setup_exception_handler
exception_app_name = "afterschool"
if app.debug:
    exception_app_name += "-dev"
setup_exception_handler(exception_app_name)


# Setup access to app,db and all db model classes from development shell.
import hgsc_utils.flask.shell_context_setup

import click_commands

# Connect Flask-Admin
admin.init_app(app)

# Load all views
from views import google_auth
from views import index
from views import afterschool_admin
from views import reports
