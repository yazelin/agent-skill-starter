# Agent Skill 入門模板：總覽

用一個最小但完整的 Skill（structured-summary）看懂「怎麼做一個 Agent Skill（Claude Code Skill）」：自動觸發、輸出穩定、精確的部分交給腳本。

## 這個範例做什麼

範例 skill 叫 `structured-summary`：把雜亂筆記（會議記錄、工作日誌、客戶訊息）整理成固定格式的結構化摘要——重點、待辦、相關日期、提及的人、關鍵數字。

## 兩段：先 ad-hoc prompt、再打包成 Skill

這份教材分兩段對照：

- **Part 1（baseline，`part1_adhoc/`）** — 「還沒做成 skill」的做法：每次要整理筆記，就把一長串 prompt 貼給 AI，後面接上你的原始文字。會動，但每次重貼、結果不一致、精確欄位靠模型用眼睛抓。
- **Part 2（成品，`skills/structured-summary/`）** — 把同一套做法**打包成一個 Skill**：`SKILL.md`（YAML frontmatter 的 name/description 讓它自動觸發）+ `scripts/extract.py`（確定性抽取 dates/mentions/todos/numbers）+ `references/format.md`（輸出格式，progressive disclosure）。

先做過 Part 1 痛一次，再看 Part 2 怎麼把痛點一個個解掉——你會更清楚 Skill 到底替你省了什麼。

## 核心心法

**需要判斷的留給模型，需要精確的交給腳本。**

- `重點`（3 到 5 條）需要理解與取捨 → 交給模型。
- `待辦 / 日期 / 提及 / 數字` 要「完整、不漏、每次一致」→ 交給 `scripts/extract.py`。

這就是這個範本想讓你帶走的一句話。

## 適合誰

想讓 Claude Code 在對的時機自動套用自家固定流程（整理、轉檔、檢查、產報告）的開發者；想搞懂 Skill 由哪幾個檔組成、怎麼被載入、怎麼測的人。

## 你會做出什麼

- 一個會自動觸發的 Claude Code Skill
- 一支純標準函式庫、零相依、確定性的抽取腳本
- 一份 progressive disclosure 的輸出格式參考檔
- 免 key 的確定性測試（驗 frontmatter + 引用檔存在 + 跑腳本斷言抽取）

## 建議學習方式

1. 先照 `01-quickstart.md` 跑起來，確認測試全綠。
2. 再看 `02-architecture.md` 理解 Skill 由哪幾個檔組成、怎麼自動觸發。
3. 照 `03-step-by-step.md` 從零把 `structured-summary` 親手做一遍。
4. 準備裝進 Claude Code 時看 `04-deployment.md`。

## 免費與付費怎麼分

這個 repo 公開最小可跑版本與完整操作步驟。真正適合工作坊或顧問的部分，是陪你把這套流程改成你自家的場景。

- 免費：可重現的 starter、教學文件、基本安裝方向。
- 付費工作坊：手把手解問題、看你的腳本與設定、一起改成你的使用場景。
- 企業顧問：需求訪談、把內部流程設計成一組 Skill、部署與維運規劃。
