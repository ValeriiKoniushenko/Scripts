#!/bin/sh
set -eu

if [ "$#" -lt 2 ]; then
  echo "usage: $0 <timeout> <command> [arguments...]" >&2
  exit 2
fi

timeout=$1
shift
exec timeout "$timeout" "$@"
