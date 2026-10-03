#!/bin/sh
set -eu

if [ "$#" -ne 2 ]; then
  echo "usage: $0 <ci-config> <check>" >&2
  exit 2
fi

. "$1"
check=$2
set --
# shellcheck disable=SC2086
for path in $CI_CHANGED_FILE_EXCLUDES; do set -- "$@" --exclude "$path"; done

case "$check" in
  copyright)
    python3 -m scripts.ci.gitea.check_copyright "$@" \
      --report-path "$RUNNER_TEMP/copyright-report.json" \
      --start-year "$CI_COPYRIGHT_START_YEAR" --holder "$CI_COPYRIGHT_HOLDER" \
      --license-line "$CI_COPYRIGHT_LICENSE_LINE_1" \
      --license-line "$CI_COPYRIGHT_LICENSE_LINE_2" \
      --license-line "$CI_COPYRIGHT_LICENSE_LINE_3" \
      --license-line "$CI_COPYRIGHT_LICENSE_LINE_4" \
      --license-line "$CI_COPYRIGHT_LICENSE_LINE_5" \
      --license-line "$CI_COPYRIGHT_LICENSE_LINE_6"
    ;;
  publish-copyright)
    python3 -m scripts.ci.gitea.publish_copyright --report-path "$RUNNER_TEMP/copyright-report.json"
    ;;
  format)
    python3 -m scripts.ci.gitea.check_clang_format "$@"
    ;;
  tidy)
    python3 -m scripts.ci.gitea.check_clang_tidy "$@" \
      --build-dir "$CI_GCC_BUILD_DIR" --fail-on error
    ;;
  capture-ui)
    timeout 2m python3 -m scripts.ci.gitea.capture_game_ui \
      --executable "$CI_GCC_BUILD_DIR/$CI_GAME_EXECUTABLE" \
      --output "$RUNNER_TEMP/$CI_GAME_SCREENSHOT_NAME" \
      --window-cache "$CI_GAME_WINDOW_CACHE" \
      --environment "$CI_GAME_HEADLESS_ENVIRONMENT"
    ;;
  tests)
    timeout 3m "$CI_GCC_BUILD_DIR/$CI_TEST_EXECUTABLE"
    ;;
  coverage)
    export CCACHE_DIR="$CI_COVERAGE_CCACHE_DIR"
    timeout 45m "$(dirname "$0")/build_cmake.sh" \
      "$CI_COVERAGE_BUILD_DIR" "$CI_JOBS" "$CI_COVERAGE_TARGET"
    ;;
  publish-coverage)
    python3 -m scripts.ci.gitea.publish_coverage \
      --summary "$CI_COVERAGE_BUILD_DIR/coverage-report/summary.json" \
      --report "$CI_COVERAGE_BUILD_DIR/coverage-report/index.html"
    ;;
  valgrind-tests)
    timeout 5m python3 -m scripts.ci.gitea.check_valgrind \
      --executable "$CI_GCC_BUILD_DIR/$CI_TEST_EXECUTABLE" \
      --suppressions "$CI_VALGRIND_SUPPRESSIONS" --verbose
    ;;
  valgrind-game)
    timeout 8m python3 -m scripts.ci.gitea.run_game_valgrind \
      --executable "$CI_GCC_BUILD_DIR/$CI_GAME_EXECUTABLE" \
      --timeout "$CI_GAME_TIMEOUT_SECONDS" \
      --suppressions "$CI_VALGRIND_SUPPRESSIONS" \
      --window-cache "$CI_GAME_WINDOW_CACHE" \
      --environment "$CI_GAME_HEADLESS_ENVIRONMENT"
    ;;
  *) echo "unknown CI check: $check" >&2; exit 2 ;;
esac
