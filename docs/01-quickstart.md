# Agent Skill 入門模板：快速開始

這份文件帶你「不卡住、走完一遍、知道自己成功了」。每一步都有：要打的指令 → 跑完的真實輸出 → 成功的話你會看到什麼。

## 前置需求

- Python 3.11+
- Git
- 會用終端機
- [uv](https://docs.astral.sh/uv/)（本教學的環境管理工具）

不需要任何 API key，也不需要外部服務。這個 starter 只用 Python 標準函式庫，沒有第三方相依套件。後面所有測試都是「免 key 確定性」的——它們驗的是 skill 結構與腳本輸出，不需要真的呼叫模型。

### 安裝 uv（一次就好）

Ubuntu / macOS：

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Windows（PowerShell）：

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

裝完重開終端機，`uv --version` 印得出版本就 OK。`uv sync` 會依 `pyproject.toml` 自動建立 `.venv`（毋須手動 venv / activate），`uv run` 直接在那個環境裡執行。**以下 `uv sync` / `uv run` 在 Ubuntu 與 Windows 完全相同。**

## 這個 repo 是什麼（先讀一句）

它教你「怎麼做一個 Agent Skill」。`part1_adhoc/` 是還沒做成 skill 的 baseline；`skills/structured-summary/` 是打包好的成品 Skill。Quickstart 先讓你把成品的確定性測試跑綠，確認環境與 skill 結構都正確。

## 步驟 1：取得程式

實際指令：

```bash
git clone https://github.com/yazelin/agent-skill-starter.git
cd agent-skill-starter
uv sync
```

成功的話你會看到：clone 完成，`ls` 看得到 `skills/`、`part1_adhoc/`、`tests/`、`client_smoke_test.py`，而 `uv sync` 會建立 `.venv`（這個 starter 沒有第三方相依，所以很快）。

## 步驟 2：跑全部確定性測試（最快的驗證）

`client_smoke_test.py` 會依序跑兩支測試：

- `tests/test_skill_structure.py` — 驗 `SKILL.md` 有合法 YAML frontmatter（name + 夠具體的 description），且它引用的 `scripts/extract.py`、`references/format.md` 都真的存在。
- `tests/test_extract.py` — 用 subprocess 跑抽取腳本對 `part1_adhoc/sample_input.txt`，斷言它抓到該抓的日期、人名、待辦與帶單位的數字。

實際指令：

```bash
uv run python client_smoke_test.py
```

真實輸出（這是實際跑出來的，不是示意）：

```
== tests/test_skill_structure.py ==
OK: skill structure test passed

== tests/test_extract.py ==
OK: extract test passed
{"dates": ["2026-06-04", "2026/06/10"], "mentions": ["小華", "阿明"], "todos": ["@阿明 在 2026/06/10 前補出貨報表", "追蹤一筆 NT$12,000 的退款", "跟供應商確認下週要採購的 5 台 機器人手臂"], "numbers": ["320 台", "98%", "2 件", "NT$12,000", "5 台", "NT$ 250,000"]}

OK: all checks passed
```

成功的話你會看到：兩段各自的 `OK:`，最後一行 `OK: all checks passed`。任何一項失敗，`client_smoke_test.py` 會以非 0 結束（方便 CI 把關）。

## 步驟 3：直接跑抽取腳本（看見「精確的部分」）

Skill 的核心心法是「精確的部分交給腳本」。你可以不透過測試，直接把雜亂筆記丟給腳本，看它吐出穩定的 JSON：

實際指令：

```bash
uv run python skills/structured-summary/scripts/extract.py part1_adhoc/sample_input.txt
```

真實輸出：

```json
{
  "dates": ["2026-06-04", "2026/06/10"],
  "mentions": ["小華", "阿明"],
  "todos": ["@阿明 在 2026/06/10 前補出貨報表", "追蹤一筆 NT$12,000 的退款", "跟供應商確認下週要採購的 5 台 機器人手臂"],
  "numbers": ["320 台", "98%", "2 件", "NT$12,000", "5 台", "NT$ 250,000"]
}
```

成功的話你會看到：四個欄位 `dates / mentions / todos / numbers` 都被抓出來。重點是——**同樣的輸入，每次都吐出完全一樣的結果**。這就是為什麼這部分該寫在腳本裡，而不是塞進 prompt 讓模型用眼睛抓。

## 步驟 4：看 baseline 痛在哪（對照）

打開 `part1_adhoc/prompt.md` 與 `part1_adhoc/sample_input.txt`，把 prompt 那一整段 + sample 內容貼給 AI 看它產生摘要。會動，但你會發現：每次都要重貼這一長串、結果不一定一致、精確欄位靠模型眼睛抓、而且 AI 不會主動套用。

這正是 Part 2 用一個 Skill 解決的——`03-step-by-step.md` 會帶你親手把它做出來。

## 第一次成功的標準（整體確認）

跑完上面幾步，你應該能勾掉這份清單：

- [ ] `uv run python client_smoke_test.py` 以 `OK: all checks passed` 收尾，兩段測試各自 `OK:`。
- [ ] 直接跑 `extract.py` 對 `sample_input.txt`，吐出上面那份 JSON（四個欄位齊全）。
- [ ] 看過 `part1_adhoc/` 的 baseline，知道「沒有 skill」會痛在哪。
- [ ] 沒有把任何 secret 或本機絕對路徑誤 commit 到 GitHub。

接著看 `02-architecture.md`，理解這個 Skill 由哪幾個檔組成、又是怎麼被自動觸發的。
