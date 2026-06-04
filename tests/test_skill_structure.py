#!/usr/bin/env python3
"""Validate the skill is well-formed. No API key needed.

We cannot test "does the LLM auto-trigger this skill" without a model, but we
CAN deterministically check the structure that makes a skill valid and
discoverable: a YAML frontmatter with name + a specific description, and that
every bundled file the SKILL.md relies on actually exists.
"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
SKILL_DIR = ROOT / "skills" / "structured-summary"
SKILL = SKILL_DIR / "SKILL.md"


def main():
    assert SKILL.exists(), f"missing {SKILL}"
    text = SKILL.read_text(encoding="utf-8")

    m = re.match(r"^---\n(.*?)\n---\n", text, re.S)
    assert m, "SKILL.md must start with YAML frontmatter delimited by --- lines"
    fm = m.group(1)

    assert re.search(r"^name:\s*\S+", fm, re.M), "frontmatter needs a name"
    desc = re.search(r"^description:\s*(\S.*)", fm, re.M)
    assert desc, "frontmatter needs a description"
    assert len(desc.group(1)) >= 30, (
        "description must be specific (>=30 chars) so the skill triggers reliably"
    )

    assert (SKILL_DIR / "scripts" / "extract.py").exists(), "missing scripts/extract.py"
    assert (SKILL_DIR / "references" / "format.md").exists(), "missing references/format.md"

    print("OK: skill structure test passed")


if __name__ == "__main__":
    try:
        main()
    except AssertionError as e:
        print(f"FAIL: {e}")
        sys.exit(1)
