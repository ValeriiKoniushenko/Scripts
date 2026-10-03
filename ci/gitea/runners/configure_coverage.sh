#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "usage: $0 <ci-config>" >&2
  exit 2
fi

. "$1"
export CCACHE_DIR="$CI_COVERAGE_CCACHE_DIR"
export CMAKE_GENERATOR="$CI_CMAKE_GENERATOR"
cmake -E remove_directory "$CI_COVERAGE_BUILD_DIR"
# shellcheck disable=SC2086
"$(dirname "$0")/configure_cmake.sh" . "$CI_COVERAGE_BUILD_DIR" \
  "$CI_COVERAGE_COMPILER" "$CI_COVERAGE_BUILD_TYPE" $CI_COVERAGE_CMAKE_OPTIONS
