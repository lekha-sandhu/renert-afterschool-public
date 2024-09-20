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
export CONFIG_FILE=dev.conf

PORT=$(sed -nE \
	'/^PORT *= */ { s/^PORT *= *([0-9]+)$/\1/ ; p ; q0 } ; $q1' \
	"$CONFIG_FILE") \
	|| die "error: can't find valid PORT=NNNNN settings in '$CONFIG_FILE'"


exec flask run --reload -p "$PORT" -h 127.0.0.1
