#!/bin/sh
set -eu

if [ "$#" -lt 2 ]; then
  echo "usage: $0 <jobs> <submodule>..." >&2
  exit 2
fi

jobs=$1
shift

cache_key="$(date -u +%G-%V)-$(git ls-tree HEAD -- "$@" | sha256sum | cut -d' ' -f1)"
cache_stamp=.git/third-party-submodules.cache

if [ ! -f "$cache_stamp" ] || [ "$(cat "$cache_stamp")" != "$cache_key" ] || \
   git submodule status --recursive "$@" | grep -Eq '^[-+U]'; then
  git submodule update --init --recursive --depth 1 --jobs "$jobs" "$@"
  printf '%s\n' "$cache_key" > "$cache_stamp"
fi
