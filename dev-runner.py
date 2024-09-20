#!/usr/bin/env python3

# Copyright (C) 2020-2024 House Gordon Software Company LTD
# All Rights Reserved
# License: Proprietary

"""
This helper script is used to run a local development flask server,
and auto-initialize a default "dev.conf" file if needed.

Conceptually similar to "run-dev.sh", but should (hopefully)
work on windows machines from inside VS-Code without needing batch files.
"""

import sys
from random import choice
from string import ascii_letters
import os.path
from os import environ
from configobj import ConfigObj

default_dev_conf="""
## NOTE: This is a Python file.
## Only items in UPPER-CASE will be used.
## see: https://flask.palletsprojects.com/en/1.1.x/config/#configuring-from-files

# Max HTTP POST upload file-size, ~100K
MAX_CONTENT_LENGTH = 100000

# CSRF private key
SECRET_KEY = '{secret_key}'

SQLALCHEMY_DATABASE_URI="postgresql://{user}@localhost/public_school?application_name=DEV_{user}"

SQLALCHEMY_TRACK_MODIFICATIONS=False
#SQLALCHEMY_ECHO=True

# Debug Toolbar: don't intercept HTTP redirects
DEBUG_TB_INTERCEPT_REDIRECTS=False

GOOGLE_AUTH_BYPASS_USER="assaf.gordon@renertschool.ca"

ENABLE_IMPERSONATE_USER=True

# This setting is an exception: it is NOT used by the flask python code,
# but by the run-dev.sh/run-prod.sh/dev-runner.py scripts.
PORT=5000
"""

if not os.path.exists("dev.conf"):
    # Create a default "dev.conf"
    user = input("*** ENTER your extoasis/database username (typically your first name): ")
    if not user.strip():
        sys.exit("missing username - aborting.")

    secret_key = ''.join([choice(ascii_letters) for i in range(32)])

    # Generate the configuration content
    conf = default_dev_conf.format(user=user, secret_key=secret_key)

    # Write the new conf file
    f = open("dev.conf","wt")
    f.write(conf)
    f.close()

# Read the "PORT=" value from "dev.conf"
cfg = ConfigObj("dev.conf")
port = cfg.get("PORT")

# Run flask (this emulates "flask run ...." from the command line,
# just like "run-dev.sh" is doing).
os.environ["CONFIG_FILE"] = "dev.conf"
os.environ["FLASK_DEBUG"] = "1"

from app import app

import logging
app.logger.setLevel(logging.DEBUG)

app.run(debug=True,host='127.0.0.1',port=port,use_reloader=True)
