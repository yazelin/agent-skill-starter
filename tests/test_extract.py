#!/usr/bin/env python3
"""Deterministic test for the extractor. No API key, no network.

Asserts properties (presence) rather than brittle full-equality, but the
extractor is fully deterministic, so this is repeatable.
"""
import json
import pathlib
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = ROOT / "skills" / "structured-summary" / "scripts" / "extract.py"
SAMPLE = ROOT / "part1_adhoc" / "sample_input.txt"


def main():
    out = subprocess.check_output(
        [sys.executable, str(SCRIPT), str(SAMPLE)], text=True
    )
    r = json.loads(out)

    assert "2026-06-04" in r["dates"], r["dates"]
    assert "2026/06/10" in r["dates"], r["dates"]

    assert "阿明" in r["mentions"], r["mentions"]
    assert "小華" in r["mentions"], r["mentions"]

    assert any("退款" in t for t in r["todos"]), r["todos"]
    assert any("出貨報表" in t for t in r["todos"]), r["todos"]
    assert any("機器人" in t for t in r["todos"]), r["todos"]

    joined = " ".join(r["numbers"])
    assert "%" in joined, r["numbers"]            # 98%
    assert any("台" in n for n in r["numbers"]), r["numbers"]   # 320 台 / 5 台
    assert any("NT$" in n for n in r["numbers"]), r["numbers"]  # NT$12,000 / NT$ 250,000

    print("OK: extract test passed")
    print(json.dumps(r, ensure_ascii=False))


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"FAIL: assertion failed -> {e}")
        sys.exit(1)
