#!/usr/bin/env python3
"""Validate implementation and release evidence for specification requirements."""

import argparse
import csv
import re
import sys
from pathlib import Path


CSV_FIELDS = [
    "requirement_id",
    "requirement_summary",
    "mandatory",
    "implementation_artifact",
    "implementation_evidence",
    "verification_id",
    "verification_evidence",
    "status",
]
ID_PATTERN = re.compile(r"REQ-[0-9]{3}")
BULLET_REQUIREMENT = re.compile(
    r"^\s*-\s+\*\*(REQ-[0-9]+) \((mandatory|optional)\):\*\*"
)
TABLE_ID = re.compile(r"REQ-[0-9]+")
BOOLEAN_VALUES = {
    "true": True,
    "yes": True,
    "1": True,
    "mandatory": True,
    "false": False,
    "no": False,
    "0": False,
    "optional": False,
}


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--spec", required=True, type=Path, help="approved Markdown specification")
    parser.add_argument("--traceability", required=True, type=Path, help="requirement traceability CSV")
    parser.add_argument(
        "--release",
        action="store_true",
        help="require verification IDs and evidence for mandatory requirements",
    )
    return parser.parse_args(argv)


def read_requirements(spec_path, errors):
    try:
        lines = spec_path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError):
        errors.append("cannot read specification file")
        return {}

    requirements = {}
    for line_number, line in enumerate(lines, start=1):
        match = BULLET_REQUIREMENT.match(line)
        requirement_id = None
        mandatory = None

        if match:
            requirement_id = match.group(1)
            mandatory = match.group(2) == "mandatory"
        elif re.match(r"^\s*-\s+\*\*REQ-", line):
            errors.append(f"malformed requirement definition on spec line {line_number}")
            continue
        elif line.lstrip().startswith("|"):
            cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
            if cells and TABLE_ID.fullmatch(cells[0]):
                requirement_id = cells[0]
                if len(cells) < 2 or cells[1].lower() not in BOOLEAN_VALUES:
                    errors.append(f"malformed requirement definition on spec line {line_number}")
                    continue
                mandatory = BOOLEAN_VALUES[cells[1].lower()]
            elif cells and cells[0].startswith("REQ-"):
                errors.append(f"malformed requirement definition on spec line {line_number}")
                continue

        if requirement_id is None:
            continue
        if not ID_PATTERN.fullmatch(requirement_id):
            errors.append(f"malformed requirement identifier {requirement_id} on spec line {line_number}; expected REQ-NNN")
            continue
        if requirement_id in requirements:
            errors.append(f"duplicate requirement definition {requirement_id}")
            continue
        requirements[requirement_id] = mandatory

    if not requirements:
        errors.append("specification contains no REQ-NNN requirement definitions")
    return requirements


def read_traceability(traceability_path, requirements, release, errors):
    try:
        source = traceability_path.open(encoding="utf-8", newline="")
    except OSError:
        errors.append("cannot read traceability CSV")
        return set()

    covered = set()
    with source:
        try:
            reader = csv.DictReader(source)
            if reader.fieldnames != CSV_FIELDS:
                errors.append("traceability CSV header does not match the required eight columns and order")
                return covered

            for line_number, row in enumerate(reader, start=2):
                if None in row or any(value is None for value in row.values()):
                    errors.append(f"malformed CSV row {line_number}: column count does not match header")
                    continue
                requirement_id = (row["requirement_id"] or "").strip()
                if not ID_PATTERN.fullmatch(requirement_id):
                    errors.append(f"invalid requirement identifier on CSV row {line_number}; expected REQ-NNN")
                    continue
                if requirement_id not in requirements:
                    errors.append(f"unknown requirement {requirement_id} on CSV row {line_number}")
                    continue
                if requirement_id in covered:
                    errors.append(f"duplicate mapping for {requirement_id}")
                    continue
                covered.add(requirement_id)

                mandatory_text = (row["mandatory"] or "").strip().lower()
                if mandatory_text not in BOOLEAN_VALUES:
                    errors.append(f"invalid mandatory value for {requirement_id}; use true or false")
                    continue
                mandatory = BOOLEAN_VALUES[mandatory_text]
                if mandatory != requirements[requirement_id]:
                    errors.append(f"mandatory value does not match specification for {requirement_id}")
                    continue
                if not (row["requirement_summary"] or "").strip():
                    errors.append(f"requirement_summary is missing for {requirement_id}")

                if mandatory:
                    for field in ("implementation_artifact", "implementation_evidence"):
                        if not (row[field] or "").strip():
                            errors.append(f"{field} is missing for mandatory requirement {requirement_id}")
                    if release:
                        for field in ("verification_id", "verification_evidence"):
                            if not (row[field] or "").strip():
                                errors.append(f"{field} is missing for mandatory requirement {requirement_id}")
        except (csv.Error, UnicodeError):
            errors.append("malformed traceability CSV")

    for requirement_id, mandatory in requirements.items():
        if mandatory and requirement_id not in covered:
            errors.append(f"missing mandatory requirement {requirement_id}")
    return covered


def main(argv=None):
    args = parse_args(argv)
    errors = validate_traceability(args.spec, args.traceability, args.release)
    if errors:
        for error in errors:
            print(f"traceability_check: {error}", file=sys.stderr)
        return 1

    requirements = read_requirements(args.spec, [])
    mandatory_count = sum(requirements.values())
    print(f"Traceability check passed ({mandatory_count} mandatory requirements covered).")
    return 0


def validate_traceability(spec_path, traceability_path, release=False):
    errors = []
    requirements = read_requirements(Path(spec_path), errors)
    read_traceability(Path(traceability_path), requirements, release, errors)
    return errors


if __name__ == "__main__":
    raise SystemExit(main())
