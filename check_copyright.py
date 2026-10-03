#!/usr/bin/env python3
"""Check that each provided file starts with exactly one copyright header."""

from __future__ import annotations

import argparse
from datetime import date
import re
import sys
from pathlib import Path


COPYRIGHT_RE = re.compile(rb"\bcopyright\b", re.IGNORECASE)
DEFAULT_LICENSE_LINES = (
    b"//\n",
    b'// Licensed under the Apache License, Version 2.0 (the "License");\n',
    b"// you may not use this file except in compliance with the License.\n",
    b"// You may obtain a copy of the License at\n",
    b"//\n",
    b"//     http://www.apache.org/licenses/LICENSE-2.0\n",
)
PROJECT_LINE_RE = re.compile(rb"// [^\r\n]+\n")
COPYRIGHT_LINE_RE = re.compile(
    rb"// Copyright (\d{4})-(\d{4}) (.+?)(?:\r\n|\n)?"
)


class CopyrightPolicy:
    def __init__(self, start_year: int, holder: str, license_lines: tuple[bytes, ...]) -> None:
        self.start_year = start_year
        self.holder = holder
        self.license_lines = license_lines

    @property
    def current_year(self) -> int:
        return date.today().year

    @property
    def expected_lines(self) -> tuple[bytes, ...]:
        copyright_line = (
            f"// Copyright {self.start_year}-{self.current_year} {self.holder}\n"
        ).encode("utf-8")
        return (copyright_line, *self.license_lines)


DEFAULT_POLICY = CopyrightPolicy(2018, "Valerii Koniushenko", DEFAULT_LICENSE_LINES)


def display_line(line: bytes) -> str:
    return line.decode("utf-8", errors="backslashreplace").replace("\n", r"\n")


def check_file(path: Path, policy: CopyrightPolicy = DEFAULT_POLICY) -> list[str]:
    try:
        content = path.read_bytes()
    except OSError as error:
        return [f"{path}: cannot read file: {error}"]

    content = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")

    copyright_matches = list(COPYRIGHT_RE.finditer(content))
    if not copyright_matches:
        return [f"{path}: copyright notice is missing"]

    if len(copyright_matches) != 1:
        line_numbers = [
            content.count(b"\n", 0, match.start()) + 1
            for match in copyright_matches
        ]
        return [
            f"{path}: expected exactly one copyright notice, found "
            f"{len(copyright_matches)} at lines "
            + ", ".join(map(str, line_numbers))
        ]

    lines = content.splitlines(keepends=True)
    match = copyright_matches[0]
    copyright_index = content.count(b"\n", 0, match.start())
    actual_line = lines[copyright_index]
    issues: list[str] = []

    if copyright_index != 1:
        issues.append(
            f"{path}:{copyright_index + 1}: copyright line must be line 2; "
            "the header must start at byte 0 on line 1"
        )

    year_match = COPYRIGHT_LINE_RE.fullmatch(actual_line)
    if year_match is not None:
        actual_start_year = int(year_match.group(1))
        actual_year = int(year_match.group(2))
        actual_holder = year_match.group(3).decode("utf-8", errors="replace")
        if actual_start_year != policy.start_year or actual_holder != policy.holder:
            issues.append(
                f"{path}:{copyright_index + 1}: invalid copyright holder or start year; "
                f"expected `{policy.start_year} {policy.holder}`"
            )
        if actual_year != policy.current_year:
            issues.append(
                f"{path}:{copyright_index + 1}: invalid copyright year "
                f"{actual_year}; expected `{policy.current_year}`"
            )

    if issues:
        return issues

    project_offset = lines[0].find(b"// ")
    if project_offset > 0:
        return [
            f"{path}: copyright header starts at byte {project_offset}; "
            "expected byte 0"
        ]

    if PROJECT_LINE_RE.fullmatch(lines[0]) is None:
        return [
            f"{path}:1: header text mismatch; expected `// <PROJECT_NAME>\\n`, "
            f"found `{display_line(lines[0])}`"
        ]

    for line_number, expected in enumerate(policy.expected_lines, start=2):
        if len(lines) < line_number:
            return [
                f"{path}: header is incomplete at line `{line_number}`; "
                f"expected `{display_line(expected)}`"
            ]

        actual = lines[line_number - 1]
        if actual != expected:
            return [
                f"{path}:{line_number}: header text mismatch; "
                f"expected `{display_line(expected)}`, "
                f"found `{display_line(actual)}`"
            ]

    return []


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("files", nargs="+", type=Path, help="files to check")
    parser.add_argument("--start-year", type=int, default=DEFAULT_POLICY.start_year)
    parser.add_argument("--holder", default=DEFAULT_POLICY.holder)
    parser.add_argument(
        "--license-line",
        action="append",
        default=None,
        help="header line after the copyright; can repeat",
    )
    args = parser.parse_args()

    license_lines = (
        tuple(f"{line}\n".encode("utf-8") for line in args.license_line)
        if args.license_line is not None
        else DEFAULT_LICENSE_LINES
    )
    policy = CopyrightPolicy(args.start_year, args.holder, license_lines)

    issues: list[str] = []
    for path in args.files:
        if not path.is_file():
            issues.append(f"{path}: file does not exist")
            continue
        issues.extend(check_file(path, policy))

    if issues:
        for issue in issues:
            print(issue, file=sys.stderr)
        return 1

    print(f"Checked {len(args.files)} file(s): copyright notices are valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
