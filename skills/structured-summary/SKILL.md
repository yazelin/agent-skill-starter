---
name: structured-summary
description: Use when turning messy notes (meeting minutes, work logs, customer messages) into a standard structured summary with key points, action items, dates, mentions, and numbers. Runs a deterministic extractor script, then formats the result per references/format.md.
---

# Structured Summary

Turn raw, unstructured notes into a consistent summary. The precise, repetitive
parts (dates, @mentions, action items, numbers) are handled by a script so they
are complete and identical every time — you only write the judgment part.

## Steps

1. Put the raw text in a file (or use the path the user gave you).
2. Run the deterministic extractor:

   ```
   python scripts/extract.py <input-file>
   ```

   It returns JSON: `dates`, `mentions`, `todos`, `numbers`.
3. Read `references/format.md` for the exact output layout.
4. Write the summary in that layout:
   - Fill `待辦 / 相關日期 / 提及 / 關鍵數字` straight from the extractor output.
   - Write the `重點` (3–5 bullets) yourself from reading the text.

## Rules

- Do NOT hand-extract dates / mentions / todos / numbers. Always use the script,
  so the output is consistent and nothing is missed.
- Keep the section order and headings exactly as `references/format.md` defines.
