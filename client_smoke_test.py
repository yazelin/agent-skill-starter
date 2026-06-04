#!/usr/bin/env python3
"""Run all deterministic checks for this starter. No API key, no network.

Usage:
    uv run python client_smoke_test.py
    # or plain:  python3 client_smoke_test.py
"""
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent
TESTS = [
    "tests/test_skill_structure.py",
    "tests/test_extract.py",
]


def main():
    failed = 0
    for t in TESTS:
        print(f"== {t} ==")
        # Capture + print in order so the output is identical whether run in a
        # terminal (PTY) or a pipe — the docs quote this output verbatim.
        r = subprocess.run(
            [sys.executable, str(ROOT / t)], capture_output=True, text=True
        )
        sys.stdout.write(r.stdout)
        if r.stderr:
            sys.stderr.write(r.stderr)
        if r.returncode != 0:
            failed += 1
        print()
    if failed:
        print(f"FAIL: {failed} check(s) failed")
        sys.exit(1)
    print("OK: all checks passed")


if __name__ == "__main__":
    main()
