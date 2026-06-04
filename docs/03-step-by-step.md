# Agent Skill 入門模板：帶你走一遍

這份文件不是六條指路，而是帶你「從零親手做出」`structured-summary` 這個 skill：寫 `SKILL.md` → 寫 `extract.py` → 寫 `format.md` → 測試。每一步都可動手，腳本輸出都是真的跑出來貼上的。

讀之前先記住核心心法：**需要判斷的留給模型，需要精確的交給腳本。** 整個 skill 的每個檔，都是這句話的具體落實。

> 開始前請先在 repo 根目錄跑過一次 `uv sync`（uv 安裝方式見 `01-quickstart.md`）。本文所有指令都用 `uv run python ...`，會在 uv 建好的 `.venv` 裡執行；`uv sync` / `uv run` 在 Ubuntu 與 Windows 完全相同。
>
> repo 裡 `skills/structured-summary/` 已經是做好的成品。建議你跟著本文「另起一個資料夾」從零做一遍，做完跟成品對照；或邊讀邊對照成品檔，看每一塊為什麼這樣寫。

一個 skill 就是「一個資料夾 + 一份 `SKILL.md`」。我們要在 `skills/` 下做出這個結構：

```
skills/structured-summary/
├── SKILL.md
├── scripts/extract.py
└── references/format.md
```

## 步驟 1：建資料夾

skill 的資料夾名字就是 skill 名字。

```bash
mkdir -p skills/structured-summary/scripts
mkdir -p skills/structured-summary/references
```

成功的話你會看到：兩層資料夾都建好（`scripts/` 放腳本、`references/` 放參考檔）。

## 步驟 2：寫 SKILL.md 的 frontmatter（自動觸發的核心）

`SKILL.md` 最上面用 `---` 包住的 YAML 就是 frontmatter。Claude Code 平時只看得到每個 skill 的 `name` + `description`；請求對得上 description，才會把整份 `SKILL.md` 載進來。所以 description 要寫得**具體、講清楚什麼時候用**。

`skills/structured-summary/SKILL.md` 開頭：

```yaml
---
name: structured-summary
description: Use when turning messy notes (meeting minutes, work logs, customer messages) into a standard structured summary with key points, action items, dates, mentions, and numbers. Runs a deterministic extractor script, then formats the result per references/format.md.
---
```

重點：

- `name` 跟資料夾同名。
- `description` 用 `Use when ...` 開頭，把觸發情境（messy notes / meeting minutes / work logs）寫明白。太籠統模型就不知道何時套用——本範本的測試甚至要求 description 至少 30 字，逼你寫具體。

## 步驟 3：寫 SKILL.md 的 body（給模型的步驟）

frontmatter 之下是給模型看的操作說明。核心就三件事 + 一條鐵則：

```markdown
# Structured Summary

Turn raw, unstructured notes into a consistent summary. The precise, repetitive
parts (dates, @mentions, action items, numbers) are handled by a script ...

## Steps

1. Put the raw text in a file (or use the path the user gave you).
2. Run the deterministic extractor:

       python scripts/extract.py <input-file>

   It returns JSON: `dates`, `mentions`, `todos`, `numbers`.
3. Read `references/format.md` for the exact output layout.
4. Write the summary in that layout:
   - Fill 待辦 / 相關日期 / 提及 / 關鍵數字 straight from the extractor output.
   - Write the 重點 (3–5 bullets) yourself from reading the text.

## Rules

- Do NOT hand-extract dates / mentions / todos / numbers. Always use the script.
- Keep the section order and headings exactly as references/format.md defines.
```

注意 body 怎麼分工：精確四欄叫模型「直接抄 extractor 輸出」，`重點` 才叫模型「自己讀文字歸納」。這就是心法落在指令上的樣子。

## 步驟 4：寫 scripts/extract.py（確定性的那一半）

這支腳本是純標準函式庫、零相依、無網路、無 API key。同樣輸入永遠同樣輸出——這正是它該存在於腳本而不是 prompt 的理由。它用四組正規表示式各管一欄：

```python
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
```

幾個設計細節，跟 skill 心法直接呼應：

- `NUMBER_RE` 只抓「帶單位/幣別」的數字。這樣 `2026` 這種純日期數字不會被誤當成「關鍵數字」——精確的工作要做到不夾雜。
- `dates`、`mentions` 去重排序；`numbers` 去重保序；`todos` 逐條保留原句（含負責人與日期）。
- 接受檔案路徑參數，沒給就讀 stdin；輸出 `ensure_ascii=False` 的 JSON，中文不會變成跳脫碼。

完整檔見 `skills/structured-summary/scripts/extract.py`。

## 步驟 5：跑腳本，看它吐出穩定的 JSON

腳本寫好就能單獨驗——這是 skill 比純 prompt 強的地方：精確的那一半，不靠模型也能測對錯。

```bash
uv run python skills/structured-summary/scripts/extract.py part1_adhoc/sample_input.txt
```

真實輸出：

```json
{
  "dates": [
    "2026-06-04",
    "2026/06/10"
  ],
  "mentions": [
    "小華",
    "阿明"
  ],
  "todos": [
    "@阿明 在 2026/06/10 前補出貨報表",
    "追蹤一筆 NT$12,000 的退款",
    "跟供應商確認下週要採購的 5 台 機器人手臂"
  ],
  "numbers": [
    "320 台",
    "98%",
    "2 件",
    "NT$12,000",
    "5 台",
    "NT$ 250,000"
  ]
}
```

成功的話你會看到：四欄齊全，而且**再跑一次結果一字不差**。對照 `part1_adhoc/sample_input.txt` 原文（裡面混著週會內容、`@阿明`、`@小華`、`NT$12,000`、`320 台`、`98%`），你會發現它連 `NT$ 250,000` 這種中間有空白的金額都收得乾淨。

## 步驟 6：寫 references/format.md（progressive disclosure）

把輸出版面獨立成一個 reference 檔，是刻意的設計：`SKILL.md` 只描述「何時用、怎麼做」，把又長又細的格式推到「需要時才讀」的檔，平時不佔 context。

`skills/structured-summary/references/format.md` 的核心：

```markdown
## 摘要

**重點**
- （你自己讀完內容歸納 3–5 條）

**待辦**
- （逐條來自 extractor 的 todos；若該條含 @人 或日期，一併保留）

**相關日期**
- （extractor 的 dates）

**提及的人**
- （extractor 的 mentions，前面補回 @）

**關鍵數字**
- （extractor 的 numbers，含單位）
```

版面把心法寫死進結構：四個精確欄直接餵 extractor，只有 `重點` 留給模型理解與取捨。順序與標題固定，輸出才會每次一致。

## 步驟 7：寫測試，把 skill 釘死（免 key）

skill 不用真的呼叫模型也能測。本範本有兩支確定性測試：

1. `tests/test_skill_structure.py` — 驗 `SKILL.md` 有合法 frontmatter（name + 至少 30 字的 description），且引用的 `scripts/extract.py`、`references/format.md` 都存在。它測的是「這個 skill 結構合法、可被發現」。
2. `tests/test_extract.py` — 用 subprocess 跑 `extract.py` 對 `sample_input.txt`，斷言抓到 `2026-06-04`、`阿明`、含「退款」的待辦、含 `%` 與 `NT$` 的數字等。它測的是「精確那一半真的精確」。

`client_smoke_test.py` 把兩支串起來一次跑完：

```bash
uv run python client_smoke_test.py
```

真實輸出：

```
== tests/test_skill_structure.py ==
OK: skill structure test passed

== tests/test_extract.py ==
OK: extract test passed
{"dates": ["2026-06-04", "2026/06/10"], "mentions": ["小華", "阿明"], "todos": ["@阿明 在 2026/06/10 前補出貨報表", "追蹤一筆 NT$12,000 的退款", "跟供應商確認下週要採購的 5 台 機器人手臂"], "numbers": ["320 台", "98%", "2 件", "NT$12,000", "5 台", "NT$ 250,000"]}

OK: all checks passed
```

成功的話你會看到：兩段各自 `OK:`，最後 `OK: all checks passed`。任何一項失敗會以非 0 結束（CI 就靠這個把關）。

## 動手練習

換你擴一欄。建議加 **問句（questions）**：把原文裡以 `?` 或 `？` 結尾的句子抓出來，當作「待釐清事項」。

提示：

1. 在 `extract.py` 加一組正規表示式，例如 `QUESTION_RE = re.compile(r"[^。！!？?]*[？?]")`，在 `extract()` 回傳的 dict 多加一個 `"questions"` 欄。
2. 在 `references/format.md` 的版面尾端加一節 `**待釐清**`，註明來自 extractor 的 questions。
3. 在 `tests/test_extract.py` 加一條斷言（例如 `assert r["questions"]` 至少抓到某句），再跑 `uv run python client_smoke_test.py` 驗證。

驗證時若 `client_smoke_test.py` 不是以 `OK: all checks passed` 收尾，看它印的 `FAIL:` 是哪支測試——多半是新欄沒回傳，或正規表示式沒對上 sample 裡的句子。下一步看 `04-deployment.md`，把這個 skill 真的裝進 Claude Code。
