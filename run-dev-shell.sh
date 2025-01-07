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

PORT=4000

exec /usr/bin/python3 -m flask shell
