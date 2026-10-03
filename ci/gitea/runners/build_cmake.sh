#!/bin/sh
set -eu

if [ "$#" -lt 2 ]; then
  echo "usage: $0 <build-dir> <jobs> [target]" >&2
  exit 2
fi

build_dir=$1
jobs=$2
target=${3:-}

if [ -n "$target" ]; then
  cmake --build "$build_dir" --parallel "$jobs" --target "$target"
else
  cmake --build "$build_dir" --parallel "$jobs"
fi
