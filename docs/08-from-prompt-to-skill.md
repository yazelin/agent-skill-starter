# Agent Skill 入門模板：從 ad-hoc prompt 到 packaged skill（對照課）

前面你已經跑過兩個東西：

- **Part 1（`part1_adhoc/`）** — 還沒有 skill。每次要整理筆記，就把 `prompt.md` 那一長串指示貼給 AI，後面接上原始文字。
- **Part 2（`skills/structured-summary/`）** — 把那套做法打包成一個 Skill：寫一次、自動觸發、精確的部分交給腳本。

這一課把兩者擺在一起對照，讓你看清楚「打包成 skill」到底換來什麼。它是獨立的一課——你可以先只跑 Part 1，真的體會過「每次重貼、結果飄」的繁瑣，再回來看這段，對照感最強。

## 先講結論：差在哪

| 面向 | Part 1 · ad-hoc prompt（`part1_adhoc/`） | Part 2 · packaged skill（`skills/structured-summary/`） |
|---|---|---|
| 取用方式 | 每次手動貼整段指示 | 寫一次，存在 repo 裡可重用 |
| 觸發 | 你得自己記得「我有一套做法」再貼 | `SKILL.md` 的 `description` 讓模型在對的情境**自動觸發** |
| context 成本 | 每次都付一次整段指示的 token | 主檔精簡，格式細節用 `references/` 漸進揭露才付 |
| 精確欄位 | 日期 / `@提及` / 待辦 / 數字靠模型用眼睛抓 | 交給 `scripts/extract.py`，**確定性、不漏、每次一致** |
| 一致性 | 同份文字今天抓 6 個數字、明天 5 個 | 同輸入必同輸出 |
| 格式維護 | 改格式要在那段 prompt 裡翻 | 只動 `references/format.md`，不碰觸發邏輯 |
| 可測試 | 沒得測，全靠人眼看 | `client_smoke_test.py` 免 key 驗結構 + 抽取 |

兩條核心訊息：

1. **skill 幫你把「做法」變成資產**：可重用、會自動觸發、context 便宜、可被測試釘住。對照那段每次要重貼的 `prompt.md`，skill 版是「寫一次，之後 AI 自己在對的時候套用」。
2. **skill 不幫你決定該分工到哪**：什麼留給模型、什麼交給腳本，是你自己畫的線。`重點` 留給模型寫，`待辦 / 日期 / 提及 / 數字` 交給 `extract.py`——這條線畫對了，skill 才真的比 prompt 強。

## 對照點一：同一份輸入，同一份產出

Part 1 把 `prompt.md` + `sample_input.txt` 貼給 AI，能動，但精確欄位飄。Part 2 對同一份 `sample_input.txt` 跑 `extract.py`，得到的永遠是這份確定性結果：

```
{
  "dates": ["2026-06-04", "2026/06/10"],
  "mentions": ["小華", "阿明"],
  "todos": ["@阿明 在 2026/06/10 前補出貨報表", "追蹤一筆 NT$12,000 的退款", "跟供應商確認下週要採購的 5 台 機器人手臂"],
  "numbers": ["320 台", "98%", "2 件", "NT$12,000", "5 台", "NT$ 250,000"]
}
```

模型只接手「`重點`（3–5 條）」這個真的需要理解與取捨的部分，其餘直接填腳本輸出。這就是 ad-hoc prompt 做不到的「每次一致」。

## 對照點二：skill 內部的小對照——只有指示 vs 指示 + 腳本

就算都做成 skill，也還有一層差別：

- **只有指示的 skill**：`SKILL.md` 寫「請把日期、@提及、待辦、數字都完整抓出來」，但抓的動作還是模型在做。這比 ad-hoc prompt 好在「會自動觸發、可重用」，但精確欄位**仍然會飄**，因為抓取本身沒有確定性。
- **指示 + 腳本的 skill（本範例）**：`SKILL.md` 叫模型先跑 `scripts/extract.py` 拿確定性結果，再用結果填欄位。`SKILL.md` 甚至明文禁止模型自己手抓：

  ```
  - Do NOT hand-extract dates / mentions / todos / numbers. Always use the script,
    so the output is consistent and nothing is missed.
  ```

差別就是這句：**把需要判斷的留給模型，把需要精確的交給腳本。** 「只有指示」解決了重用與觸發，「指示 + 腳本」才同時解決了精確與一致。一個 skill 值不值得加腳本，就看它有沒有「該完整不漏、規則明確、能用 code 100% 重現」的欄位。

## 怎麼自己驗證這層差異

跑全套免 key 確定性測試，看 Part 2 的結構與抽取都被釘住：

```
git clone https://github.com/yazelin/agent-skill-starter.git
cd agent-skill-starter
uv sync
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

`test_skill_structure.py` 驗 frontmatter 合法且引用檔存在（讓 skill 可觸發、不撲空），`test_extract.py` 跑腳本斷言抽取正確（讓精確欄位每次一致）——這兩件事正是 ad-hoc prompt 沒辦法驗的。

## 延伸資源 · Awesome Skills

想看更多寫好的 skill 長什麼樣、學別人怎麼分工：

- **anthropics/skills**（官方）— https://github.com/anthropics/skills
- **obra/superpowers**（社群）— https://github.com/obra/superpowers

讀別人的 skill 時，建議帶著本課的兩個問題去看：它的 `description` 是怎麼寫到會自動觸發的？它把哪些活交給腳本、哪些留給模型？
