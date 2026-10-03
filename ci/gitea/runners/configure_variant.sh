#!/bin/sh
set -eu

if [ "$#" -ne 2 ]; then
  echo "usage: $0 <ci-config> <gcc|clang>" >&2
  exit 2
fi

. "$1"
variant=$2

case "$variant" in
  gcc)
    compiler=$CI_GCC_COMPILER
    build_type=$CI_GCC_BUILD_TYPE
    build_dir=$CI_GCC_BUILD_DIR
    ccache_dir=$CI_GCC_CCACHE_DIR
    options=$CI_GCC_CMAKE_OPTIONS
    ;;
  clang)
    compiler=$CI_CLANG_COMPILER
    build_type=$CI_CLANG_BUILD_TYPE
    build_dir=$CI_CLANG_BUILD_DIR
    ccache_dir=$CI_CLANG_CCACHE_DIR
    options=$CI_CLANG_CMAKE_OPTIONS
    ;;
  *) echo "unsupported variant: $variant" >&2; exit 2 ;;
esac

export CCACHE_DIR="$ccache_dir"
export CMAKE_GENERATOR="$CI_CMAKE_GENERATOR"
# shellcheck disable=SC2086
"$(dirname "$0")/configure_cmake.sh" . "$build_dir" "$compiler" "$build_type" $options
