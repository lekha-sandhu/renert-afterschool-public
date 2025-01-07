# Copyright (C) 2020-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

# -*- coding: utf-8 -*-

from flask import Flask
from flask_wtf.csrf import CSRFProtect
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from flask_admin.base import MenuLink
from flask_login import LoginManager


app = Flask(__name__)

# Make CSRF object a global variable,
# so that all views could import it and do '@csrf.exempt' with ease.
# The actual flask-app initialization happens in 'mainapp.py'
# after configuration data is loaded.
csrf = CSRFProtect()

db = SQLAlchemy()

admin = Admin(name='Database-Admin',url="/admin")
admin.add_link(MenuLink(name='Back to Website', url='/'))

login_manager = LoginManager()
