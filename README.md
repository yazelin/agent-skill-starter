# Agent Skill Starter

學會做一個 Agent Skill（Claude Code Skill）：從每次重貼的 ad-hoc prompt，到一個會自動觸發、把精確的活交給腳本的 Skill。

範例 skill 叫 `structured-summary`：把雜亂的筆記（會議記錄、工作日誌、客戶訊息）整理成固定格式的結構化摘要。

## 繁中定位

**Agent Skill 入門模板** 面向台灣繁中受眾。

- 主要受眾：想把自己一套重複做法打包成 Claude Code Skill 的開發者。
- 核心承諾：用一個最小但完整的 skill，看懂 frontmatter 自動觸發、確定性腳本、progressive disclosure。
- 核心心法：**需要判斷的留給模型，需要精確的交給腳本。**
- CTA 頁：https://yazelin.github.io/agent-skill-starter/

## Part 1 vs Part 2

這個 repo 用同一個任務（整理筆記成結構化摘要）走兩段，讓你親眼看到 skill 解決了什麼。

### Part 1 · Ad-hoc baseline（`part1_adhoc/`）

「還沒做成 skill」的做法：每次要整理筆記，就把一長串指示貼給 AI，後面接上原始文字。

- `part1_adhoc/prompt.md` — 每次都要手動貼的一長串指示。
- `part1_adhoc/sample_input.txt` — 一份雜亂的會議記錄，當測試素材。

會動，但痛點明確：

- **每次都要重貼**這一長串指示，換台電腦、換對話就要再找一次。
- **結果不一致**：同樣的文字，今天抓到 5 個數字、明天抓到 4 個；格式偶爾跑掉。
- **精確的活靠 LLM 眼睛**：日期、金額、@提及這種「該完整不漏」的東西，模型偶爾會漏或看錯。
- **不會自動觸發**：你得記得「我有一套做法」，AI 不會主動套用。

### Part 2 · 打包成 Skill（`skills/structured-summary/`）

把同一套做法寫一次、自動觸發、精確的部分交給腳本。

```
skills/structured-summary/
  SKILL.md              <- YAML frontmatter(name / description)讓 skill 被發現並自動觸發
  scripts/extract.py    <- 確定性抽取 dates / mentions / todos / numbers
  references/format.md   <- 輸出格式(progressive disclosure，需要時才載入)
```

分工就是這個 skill 的重點：

- `重點`（3-5 條）需要理解與取捨 -> 交給模型自己讀完歸納。
- `待辦 / 相關日期 / 提及 / 關鍵數字` 要「完整、不漏、每次一致」-> 交給 `scripts/extract.py`。

## Quick start

本教學以 [uv](https://docs.astral.sh/uv/) 為主。`uv sync` 會依 `pyproject.toml` 自動建立 `.venv` 並把專案裝好（毋須手動 venv / activate），`uv run` 直接在那個環境裡執行。**以下 `uv sync` / `uv run` 在 Ubuntu 與 Windows 完全相同。**

先安裝 uv（一次就好）：

- Ubuntu / macOS：`curl -LsSf https://astral.sh/uv/install.sh | sh`
- Windows（PowerShell）：`powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"`

裝完重開終端機，`uv --version` 印得出版本就 OK。

```bash
git clone https://github.com/yazelin/agent-skill-starter.git
cd agent-skill-starter
uv sync
uv run python client_smoke_test.py
```

`client_smoke_test.py` 跑全部的確定性檢查，**不需要 API key、不連網**。預期輸出：

```
== tests/test_skill_structure.py ==
OK: skill structure test passed

== tests/test_extract.py ==
OK: extract test passed
{"dates": ["2026-06-04", "2026/06/10"], "mentions": ["小華", "阿明"], "todos": ["@阿明 在 2026/06/10 前補出貨報表", "追蹤一筆 NT$12,000 的退款", "跟供應商確認下週要採購的 5 台 機器人手臂"], "numbers": ["320 台", "98%", "2 件", "NT$12,000", "5 台", "NT$ 250,000"]}

OK: all checks passed
```

這個 starter 只用 Python 標準函式庫，`[project].dependencies` 是空的，所以 `uv sync` 只會建立環境、不會裝任何第三方套件。沒裝 uv 的話 `python3 client_smoke_test.py` 也能直接跑。

## Skill 結構

`SKILL.md` 的開頭是一段 YAML frontmatter，`name` 加上一段夠具體的 `description`，這就是 skill 「會不會被模型挑中並自動觸發」的關鍵。後面是給模型看的步驟：

1. 把原始文字放進一個檔案。
2. 跑確定性抽取器，拿到 `dates` / `mentions` / `todos` / `numbers` 的 JSON。
3. 讀 `references/format.md` 拿到固定版面。
4. 照版面寫摘要：精確欄位直接填腳本輸出，`重點` 自己讀完歸納。

直接跑抽取器看實際輸出：

```bash
uv run python skills/structured-summary/scripts/extract.py part1_adhoc/sample_input.txt
```

對 `part1_adhoc/sample_input.txt` 的真實輸出：

```json
{
  "dates": ["2026-06-04", "2026/06/10"],
  "mentions": ["小華", "阿明"],
  "todos": ["@阿明 在 2026/06/10 前補出貨報表", "追蹤一筆 NT$12,000 的退款", "跟供應商確認下週要採購的 5 台 機器人手臂"],
  "numbers": ["320 台", "98%", "2 件", "NT$12,000", "5 台", "NT$ 250,000"]
}
```

同一份輸入永遠得到同一份輸出 —— 這正是為什麼這段邏輯該放進腳本，而不是放進 prompt。

## 測試（免 key、不連網）

三個檔都是確定性的，不需要模型也能跑：

- `tests/test_skill_structure.py` — 驗 `SKILL.md` 有合法的 YAML frontmatter（含 `name` 與夠長的 `description`），且 `scripts/extract.py`、`references/format.md` 這些被引用的檔案真的存在。
- `tests/test_extract.py` — 實際跑 `extract.py` 對樣本，斷言抽到的 dates / mentions / todos / numbers。
- `client_smoke_test.py` — 一次跑完上面兩個，任何一個失敗就回傳非零。

CI（`.github/workflows/ci.yml`）就是 `uv sync` 後跑 `client_smoke_test.py`，所以這套檢查在本機與 GitHub 上行為一致。

## 延伸資源

- 官方 Awesome Skills：https://github.com/anthropics/skills
- 社群 superpowers：https://github.com/obra/superpowers

## Learn / get help

這個 repo 也是工作坊與顧問的 CTA 頁：

- GitHub Pages：https://yazelin.github.io/agent-skill-starter/
- 網頁版教學：https://yazelin.github.io/agent-skill-starter/tutorial.html
- Contact：yaze.lin.j303@gmail.com

## License

MIT

## Brand / CTA design

- Landing page：https://yazelin.github.io/agent-skill-starter/
- 設計理念：[DESIGN.md](DESIGN.md)

---

## 關於作者

這個範本由 **林亞澤（Yaze Lin）** 維護 — 出身機電自動化系統整合，現在把同一套工程方法用在 AI 產品上。

- 任職於 **擎添工業 ChingTech**（1984 年成立的機電自動化公司：PLC 程式、機械手臂、AGV 無人搬運、半導體封測／PCB／面板／光學產線整合）。
- 技術筆記與更多範例：[yazelin.github.io](https://yazelin.github.io) · GitHub [@yazelin](https://github.com/yazelin)

## 從範本到正式產品

> 把「需要精確的交給腳本、需要判斷的留給模型」這條線做大，我們做成了 AgentOS（agent 治理）與 Mori Desktop（個人 AI 管家）。

如果你想看同樣的想法做成正式、上線中的產品：

- **CTOS** — 企業 AI 工作平台：macOS 風格 Web 桌面、知識庫 RAG 檢索、產業專屬 Agent、LINE Bot 整合，資料留在台灣。[ching-tech.com](https://ching-tech.com) · [品牌站](https://ching-tech.github.io)
- **CTOS-Lite / CT JINN** — 把公司裝進 LINE 的個人版 AI 助理，加 LINE 即可試用：[@285fjkky](https://line.me/R/ti/p/@285fjkky)
- **Mori Desktop** — 個人 AI 管家桌面應用（Tauri 2 + Rust + React）：[github.com/yazelin/mori-desktop](https://github.com/yazelin/mori-desktop)
- **AgentOS** — 跨 CLI 的 agent 治理平台（開發中）

> 想把這個範本落地成你自己的一套 Skill，或想上一堂從 ad-hoc prompt 到打包 skill 的課？
> 來信 yaze.lin.j303@gmail.com，或追蹤上面的連結。
