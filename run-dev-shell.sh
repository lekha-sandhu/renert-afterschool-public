#!/bin/sh

export FLASK_ENV=development
export FLASK_DEBUG=1
export FLASK_APP=app:app
export CONFIG_FILE=dev.conf

flask shell
