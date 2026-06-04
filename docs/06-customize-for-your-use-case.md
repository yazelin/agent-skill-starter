# Agent Skill 入門模板：改成你的使用場景

這個範例 skill（`skills/structured-summary/`）做的是「雜亂筆記 → 固定格式摘要」。同一套骨架可以改成你自己的 skill。一個 skill 就三塊：

- `SKILL.md` — frontmatter（觸發）+ 步驟 + 鐵則。
- `scripts/` — 確定性的精確抽取 / 轉換。
- `references/` — 漸進揭露的格式、查表、長範例。

要改成你的場景，就是分別改這三塊。下面照「最小改動 → 較大改動」排。

## 改造一：換 `extract.py` 的抽取規則（最常改）

`scripts/extract.py` 用幾條正則抽 `dates / mentions / todos / numbers`。把它換成你領域真正要「完整不漏」的欄位即可。

現在的數字規則（`NUMBER_RE`）只認帶單位 / 幣別的數字，避免把日期數字誤當成數量：

```python
NUMBER_RE = re.compile(
    r"(NT\$\s?\d[\d,]*(?:\.\d+)?|\d[\d,]*(?:\.\d+)?\s*(?:%|元|個|台|人|位|件|小時|hrs?|hours?|kg))",
    re.IGNORECASE,
)
```

常見改法：

- 改幣別 / 單位：把 `NT\$` 換成 `US\$` 或 `¥`，把 `台|人|位|件` 換成你產業的單位（`箱|棧板|工單|ppm` ...）。
- 改抽取對象：例如抽「料號」「工單號」「機台編號」，就照 `MENTION_RE` / `DATE_RE` 的寫法加一條新的正則，並在 `extract()` 回傳的 dict 多一個 key。
- 改待辦判斷：`TODO_RE` 現在認 `-` / `*` / `[ ]` / `TODO` / `待辦` / `要做` / `需要` / `action item` 開頭的行，可以加你團隊習慣的關鍵字。

改完務必更新 `tests/test_extract.py` 的斷言，讓它驗你新欄位真的抽得到，並跑一次：

```
uv run python skills/structured-summary/scripts/extract.py part1_adhoc/sample_input.txt
```

原樣 repo 對 `sample_input.txt` 的真實輸出長這樣（改規則後這份會跟著變，這就是你要在測試裡釘住的東西）：

```
{
  "dates": ["2026-06-04", "2026/06/10"],
  "mentions": ["小華", "阿明"],
  "todos": ["@阿明 在 2026/06/10 前補出貨報表", "追蹤一筆 NT$12,000 的退款", "跟供應商確認下週要採購的 5 台 機器人手臂"],
  "numbers": ["320 台", "98%", "2 件", "NT$12,000", "5 台", "NT$ 250,000"]
}
```

## 改造二：換 `references/format.md` 的輸出版面

輸出長相全在 `references/format.md`，`SKILL.md` 只說「Read references/format.md for the exact output layout」。要改格式**只動這一個檔**，不碰觸發邏輯。

例如把摘要改成「客服回覆草稿」「巡檢日報」「採購簽核單」，就把 `references/format.md` 裡的欄位順序 / 標題換掉。原則照舊：

- 需要理解、取捨、歸納的欄位（像 `重點`）→ 由模型寫。
- 要完整不漏、每次一致的欄位（像 `待辦 / 日期 / 數字`）→ 直接填 `extract.py` 的輸出。

## 改造三：加 `references/`（漸進揭露更多規則）

當規則變多（多種文件類型、各自版面、一堆邊角案例），不要全塞回 `SKILL.md`。在 `references/` 多開檔：`references/format-daily.md`、`references/glossary.md`、`references/examples.md` ...，在 `SKILL.md` 用一句「Read references/xxx.md when ...」分流。`SKILL.md` 永遠保持精簡，每次觸發才便宜。

## 改造四：改 `SKILL.md` 的 frontmatter（決定何時觸發）

換場景後最重要的是改 `description`，否則 skill 對不上你新的使用情境就不會被叫起來。寫成「Use when <你的情境> ...」，列出真實會出現的講法。`name` 也換成你的 skill 名（小寫、連字號）。

改完跑結構測試確認 frontmatter 與引用檔都還合法：

```
uv run python tests/test_skill_structure.py
```

## 改造原則

- 一次只改一個層次：先改 `extract.py`，再改 `format.md`，再動 `description`。
- 先保留原本可跑的範例，另開 branch 做實驗。
- 每改一條抽取規則，就改一條 `tests/test_extract.py` 斷言把它釘住。
- 動完任何一塊都跑 `uv run python client_smoke_test.py`，確認結構測試 + 抽取測試還綠。
- 需要判斷的留給模型，需要精確的交給腳本——換場景也別破壞這條分工。

## 適合拿來做課程 / 工作坊的題目

- 從零跑起這個 starter（`uv sync` → `client_smoke_test.py`）。
- 把 `structured-summary` 改成自己團隊真實的文件流程。
- 設計一條新的抽取規則，並用測試把它釘住。
- 比較 Part 1 ad-hoc prompt 與 Part 2 packaged skill 的差異（見 `08-from-prompt-to-skill.md`）。
- 現場 debug 學員的 skill 為什麼不觸發。
