#!/bin/sh

die()
{
	base=$(basename "$0")
	echo "$base: error: $*" >&2
	exit 1
}

export FLASK_ENV=development
export FLASK_DEBUG=1
export FLASK_APP=app:app
export CONFIG_FILE=dev.conf

PORTLINE=$(grep "^PORT *= *[0-9][0-9]*$" "$CONFIG_FILE") \
	|| die "can't find valid PORT=NNNN settings in config file '$CONFIG_FILE'"
PORT=$(echo "$PORTLINE" | sed --posix 's/.*= *//')

exec /usr/bin/env python3 -m flask run --reload -p "$PORT" -h 127.0.0.1
