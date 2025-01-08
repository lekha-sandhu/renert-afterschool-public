#!/bin/sh

die()
{
	base=$(basename "$0")
	echo "$base: error: $*" >&2
	exit 1
}

export FLASK_ENV=production
export FLASK_DEBUG=
export FLASK_APP=app:app
export CONFIG_FILE=prod.conf

NAME="Afterschool"
PORT=$(sed -nE \
	'/^PORT *= */ { s/^PORT *= *([0-9]+)$/\1/ ; p ; q0 } ; $q1' \
	"$CONFIG_FILE") \
	|| die "error: can't find valid PORT=NNNNN settings in '$CONFIG_FILE'"

WORKERS=2

# Change to /var/log/app/ if needed.
# Logging support log-rotate (see ./contrib file)
LOGDIR=logs

# disable any internal buffering in stdio in python
export PYTHONUNBUFFERED=1

PID=afterschool-prod.pid

exec setpriv --nnp \
	gunicorn3 --reload \
	  --workers $WORKERS \
	  --capture-output \
	  -n "$NAME" \
	  -b 127.0.0.1:$PORT \
	  --access-logfile "$LOGDIR/access.log" \
	  --error-logfile "$LOGDIR/error.log" \
	  --pid "$PID" \
	  app:app
