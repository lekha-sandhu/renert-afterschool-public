from flask import Blueprint, current_app
from .gunicorn_logging_hack import test_logging_messages

logtest_blueprint = Blueprint('logtest_blueprint', __name__)

@logtest_blueprint.route('/')
def index():
    marker = test_logging_messages(current_app)
    return "Messages sent to various logs, marker = %s" % marker
