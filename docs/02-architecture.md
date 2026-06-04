# Agent Skill 入門模板：架構說明

一個 Claude Code Skill 就是「一個資料夾 + 一份 `SKILL.md`」。資料夾名字是 skill 名字，`SKILL.md` 是入口，旁邊可以放腳本與參考檔。理解這份文件，你就理解了整個範本怎麼組起來。

## 核心結構

```
skills/structured-summary/
├── SKILL.md                ← 入口：YAML frontmatter + 給模型的步驟說明
├── scripts/
│   └── extract.py          ← 確定性抽取（dates / mentions / todos / numbers）
└── references/
    └── format.md           ← 輸出格式（progressive disclosure，需要時才讀）
```

對照真實檔：

- `skills/structured-summary/SKILL.md`
- `skills/structured-summary/scripts/extract.py`
- `skills/structured-summary/references/format.md`

## SKILL.md frontmatter — 自動觸發的關鍵

`SKILL.md` 最上面用 `---` 包住的 YAML 區塊就是 frontmatter。本範本實際長這樣：

```yaml
---
name: structured-summary
description: Use when turning messy notes (meeting minutes, work logs, customer messages) into a standard structured summary with key points, action items, dates, mentions, and numbers. Runs a deterministic extractor script, then formats the result per references/format.md.
---
```

兩個欄位各有任務：

- `name` — skill 的識別名字（這裡是 `structured-summary`，跟資料夾同名）。
- `description` — **這是自動觸發的核心**。Claude Code 平時只看得到每個 skill 的 name + description；當你的請求跟某個 description 對得上（例如「幫我把這份會議記錄整理成摘要」），它才會把對應的 `SKILL.md` 全文載進來照做。

所以 description 要寫得「**具體、講清楚什麼時候用**」——用 `Use when ...` 開頭，把觸發情境（messy notes / meeting minutes / work logs）講明白。寫得太籠統（例如只寫「整理文字」），模型就不知道何時該套用。`tests/test_skill_structure.py` 甚至硬性要求 description 至少 30 字，就是在逼你寫具體。

## SKILL.md body — 給模型的步驟說明

frontmatter 之下是給模型看的操作說明。本範本的 body 講三件事：

1. 把原始文字放進檔案（或用 user 給的路徑）。
2. 跑確定性抽取：`python scripts/extract.py <input-file>`，它回 JSON（`dates` / `mentions` / `todos` / `numbers`）。
3. 讀 `references/format.md` 拿到輸出版面，然後照填——精確欄位直接抄 extractor 輸出，`重點` 自己讀文字歸納。

body 還有一條鐵則：**不要手動抽日期 / 人名 / 待辦 / 數字，一律用腳本**，這樣輸出才會完整且每次一致。

## scripts/extract.py — 確定性的那一半

`extract.py` 是純標準函式庫、零相依、無網路、無 API key 的腳本。同樣的輸入永遠給同樣的輸出——這正是它該存在於腳本而不是 prompt 的理由。它用四組正規表示式各管一欄：

- `DATE_RE` — 抓 `2026-06-04`、`2026/6/4`、`6/10` 這類日期。
- `MENTION_RE` — 抓 `@名字`（ASCII 或中日韓字都吃）。
- `NUMBER_RE` — 只抓「帶單位/幣別」的數字（`NT$`、`%`、`元`、`台`、`件`、`hrs` 等），這樣純日期數字不會被誤當成「關鍵數字」。
- `TODO_RE` — 抓 bullet / checkbox / 關鍵字（`TODO`、`待辦`、`需要` 等）開頭的行。

輸出時 `dates`、`mentions` 去重排序，`numbers` 去重保序，`todos` 逐條保留原句（含負責人與日期）。

## references/format.md — progressive disclosure

`format.md` 放的是輸出版面（`## 摘要` 下的 `重點 / 待辦 / 相關日期 / 提及的人 / 關鍵數字`，順序與標題固定）。

它被獨立成一個 reference 檔，是刻意的 **progressive disclosure**：`SKILL.md` 只負責「描述何時用、怎麼做」，把又臭又長的格式細節推到一個「需要時才讀」的檔。模型只有在真的執行到「該排版了」這一步，才去讀 `format.md`，平時不佔 context。Skill 越大，這種「把細節外推到 reference」的好處越明顯。

## 資料流：一次完整觸發長什麼樣

1. 你對 Claude Code 說「把這份會議記錄整理成結構化摘要」。
2. Claude Code 比對各 skill 的 description，命中 `structured-summary`，把它的 `SKILL.md` 載進來。
3. 模型照 `SKILL.md` 步驟，跑 `scripts/extract.py` 拿到精確的 dates / mentions / todos / numbers（JSON）。
4. 模型讀 `references/format.md` 拿到版面。
5. 模型把精確欄位直接填進去，`重點` 自己讀原文歸納，輸出固定格式的摘要。

判斷的（重點）給模型、精確的（四欄）給腳本——一次完整跑完。

## 設計原則

- 需要判斷的留給模型，需要精確的交給腳本。
- description 要具體到「模型一看就知道何時用」，自動觸發才靠得住。
- 長細節外推到 reference 檔，`SKILL.md` 保持精簡（progressive disclosure）。
- 腳本零相依、確定性、可離線測——不靠模型也能驗對錯。
- 範例刻意保持小，方便你看懂後改成自己的 skill。
