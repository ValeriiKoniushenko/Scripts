#!/bin/sh
set -eu

if [ "$#" -lt 4 ]; then
  echo "usage: $0 <source-dir> <build-dir> <gcc|clang> <build-type> [cmake-options...]" >&2
  exit 2
fi

source_dir=$1
build_dir=$2
compiler=$3
build_type=$4
shift 4

case "$compiler" in
  clang) export CC=clang CXX=clang++ ;;
  gcc) export CC=gcc CXX=g++ ;;
  *) echo "unsupported compiler: $compiler" >&2; exit 2 ;;
esac

"$CXX" --version
cmake -S "$source_dir" -B "$build_dir" -G "${CMAKE_GENERATOR:-Ninja}" \
  -DCMAKE_BUILD_TYPE="$build_type" "$@"
