#!/usr/bin/env python3
"""Hash a project's approved agent specification."""

import argparse
import hashlib
import re
import sys
from pathlib import Path


def sha256_digest(value):
    if not re.fullmatch(r"[0-9a-fA-F]{64}", value):
        raise argparse.ArgumentTypeError(
            "must be a 64 hexadecimal character SHA-256 digest"
        )
    return value.lower()


def parse_args(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--project-root",
        type=Path,
        default=Path.cwd(),
        help="project directory containing .agent-factory/spec.md (default: cwd)",
    )
    parser.add_argument(
        "--approved-hash",
        type=sha256_digest,
        help="compare the current specification against this approved SHA-256",
    )
    return parser.parse_args(argv)


def calculate_spec_hash(spec_path):
    """Return the SHA-256 digest of the exact bytes in a specification file."""
    return hashlib.sha256(Path(spec_path).read_bytes()).hexdigest()


def main(argv=None):
    args = parse_args(argv)
    spec_path = args.project_root / ".agent-factory" / "spec.md"
    try:
        digest = calculate_spec_hash(spec_path)
    except OSError:
        print(
            "spec_hash: cannot read required file .agent-factory/spec.md",
            file=sys.stderr,
        )
        return 1

    if args.approved_hash is not None and digest != args.approved_hash:
        print("SPEC_CHANGED")
        return 2

    print(digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
