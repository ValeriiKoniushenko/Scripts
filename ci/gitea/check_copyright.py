#!/usr/bin/env python3
"""Run the project copyright checker on changed C/C++ files."""

import argparse
import json
import re
import sys
from pathlib import Path

sys.dont_write_bytecode = True

from .utils import get_changed_files, get_target_branch

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from scripts.check_copyright import CopyrightPolicy, DEFAULT_LICENSE_LINES, check_file


def issue_line(path: str, message: str) -> int:
    match = re.match(rf"^{re.escape(path)}:(\d+):", message)
    return int(match.group(1)) if match else 1


def issue_message(path: str, message: str) -> str:
    return re.sub(
        rf"^{re.escape(path)}(?::\d+)?:\s*",
        "",
        message,
        count=1,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base", help="branch/ref to diff against")
    parser.add_argument("--files", nargs="+", help="explicit files; skips git diff")
    parser.add_argument("--report-path", default="copyright-report.json")
    parser.add_argument("--exclude", action="append", default=[], metavar="PATH_PREFIX",
                        help="repository-relative path prefix to exclude; can repeat")
    parser.add_argument("--verbose", "-v", action="store_true")
    parser.add_argument("--start-year", type=int, required=True)
    parser.add_argument("--holder", required=True)
    parser.add_argument("--license-line", action="append", default=None,
                        help="header line after the copyright; can repeat")
    args = parser.parse_args()

    changed = get_changed_files(
        get_target_branch(args.base),
        args.files,
        args.verbose,
        tuple(args.exclude),
    )
    files = [file.path for file in changed]
    license_lines = (
        tuple(f"{line}\n".encode("utf-8") for line in args.license_line)
        if args.license_line is not None
        else DEFAULT_LICENSE_LINES
    )
    policy = CopyrightPolicy(args.start_year, args.holder, license_lines)
    issues = []
    for path in files:
        for message in check_file(Path(path), policy):
            issues.append({
                "path": path,
                "line": issue_line(path, message),
                "message": issue_message(path, message),
            })

    with open(args.report_path, "w") as report:
        json.dump({"issues": issues}, report, indent=2)

    if issues:
        for issue in issues:
            print(
                f"{issue['path']}:{issue['line']}: {issue['message']}",
                file=sys.stderr,
            )
        return 1

    print(f"Checked {len(files)} changed C/C++ file(s): copyright notices are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
