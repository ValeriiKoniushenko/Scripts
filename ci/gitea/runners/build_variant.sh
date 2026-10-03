#!/bin/sh
set -eu

if [ "$#" -lt 2 ] || [ "$#" -gt 3 ]; then
  echo "usage: $0 <ci-config> <gcc|clang> [target]" >&2
  exit 2
fi

. "$1"

case "$2" in
  gcc) build_dir=$CI_GCC_BUILD_DIR; ccache_dir=$CI_GCC_CCACHE_DIR ;;
  clang) build_dir=$CI_CLANG_BUILD_DIR; ccache_dir=$CI_CLANG_CCACHE_DIR ;;
  *) echo "unsupported variant: $2" >&2; exit 2 ;;
esac

export CCACHE_DIR="$ccache_dir"
if [ "$#" -eq 3 ]; then
  "$(dirname "$0")/build_cmake.sh" "$build_dir" "$CI_JOBS" "$3"
else
  "$(dirname "$0")/build_cmake.sh" "$build_dir" "$CI_JOBS"
fi
