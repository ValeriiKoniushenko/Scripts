#!/bin/sh
set -eu

if [ "$#" -ne 1 ]; then
  echo "usage: $0 <ci-config>" >&2
  exit 2
fi

. "$1"

git submodule sync --recursive
# shellcheck disable=SC2086
git submodule update --init --recursive --depth 1 --jobs "$CI_JOBS" $CI_BOOTSTRAP_SUBMODULES
# shellcheck disable=SC2086
"$(dirname "$0")/init_submodules.sh" "$CI_JOBS" $CI_CACHED_SUBMODULES
