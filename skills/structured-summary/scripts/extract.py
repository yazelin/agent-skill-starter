#!/usr/bin/env python3
"""Deterministic extractor for the structured-summary skill.

Reads raw text (a file path argument, or stdin) and emits JSON with the
precise, repeatable fields a skill should NOT ask the LLM to eyeball:
dates, @mentions, action items (TODOs), and numbers with units.

Pure standard library. No network, no API key. Same input -> same output,
which is exactly why this belongs in a script and not in the prompt.
"""
import json
import re
import sys

# 2026-06-04 / 2026/6/4 / 6/10
DATE_RE = re.compile(r"\b(\d{4}[-/]\d{1,2}[-/]\d{1,2}|\d{1,2}/\d{1,2})\b")
# @name  (ASCII or CJK)
MENTION_RE = re.compile(r"@([A-Za-z0-9_一-鿿]+)")
# amounts that carry a unit/currency, so plain date digits are not mistaken for "numbers"
NUMBER_RE = re.compile(
    r"(NT\$\s?\d[\d,]*(?:\.\d+)?|\d[\d,]*(?:\.\d+)?\s*(?:%|元|個|台|人|位|件|小時|hrs?|hours?|kg))",
    re.IGNORECASE,
)
# action items: bullet/checkbox/keyword led lines
TODO_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?:\[\s*\]|TODO|待辦|要做|需要|action item)[:：]?\s*(.+)$",
    re.IGNORECASE,
)


def extract(text):
    todos = []
    for line in text.splitlines():
        m = TODO_RE.match(line)
        if m:
            todos.append(m.group(1).strip())

    numbers = []
    seen = set()
    for hit in NUMBER_RE.findall(text):
        n = re.sub(r"\s+", " ", hit).strip()
        if n not in seen:
            seen.add(n)
            numbers.append(n)

    return {
        "dates": sorted(set(DATE_RE.findall(text))),
        "mentions": sorted(set(MENTION_RE.findall(text))),
        "todos": todos,
        "numbers": numbers,
    }


def main():
    if len(sys.argv) > 1:
        with open(sys.argv[1], encoding="utf-8") as f:
            text = f.read()
    else:
        text = sys.stdin.read()
    print(json.dumps(extract(text), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
