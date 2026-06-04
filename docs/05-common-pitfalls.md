# Agent Skill 入門模板：常見踩雷清單

這些是把一套做法打包成 Agent Skill（Claude Code Skill）時真的會踩到的坑，附上真實症狀與修法。範例 skill 是 `skills/structured-summary/`：把雜亂筆記整理成固定格式摘要。

## 1. description 太籠統，skill 不會自動觸發

Skill 會不會被叫起來，**完全取決於 `SKILL.md` 的 YAML frontmatter `description`**。模型靠 `name` + `description` 判斷「現在這個任務該不該用這個 skill」。寫成 `description: 整理筆記` 這種空泛的句子，模型對不上使用者真正講的話，於是 skill 安安靜靜躺在那裡不會被觸發。

對照本範例真正的寫法（`skills/structured-summary/SKILL.md`）：

```
description: Use when turning messy notes (meeting minutes, work logs, customer messages) into a standard structured summary with key points, action items, dates, mentions, and numbers. Runs a deterministic extractor script, then formats the result per references/format.md.
```

重點在「Use when ...」開頭，**把觸發情境、輸入長相、產出長相都講清楚**：會議記錄 / 工作日誌 / 客戶訊息 → 結構化摘要。情境寫得越具體，模型越敢在對的時候自動套用。

怎麼修：description 寫成「Use when <什麼情境> ... <做什麼> ...」，列出真實會出現的同義輸入（中文／英文、不同講法），不要只寫一個動詞。

本 repo 的 `tests/test_skill_structure.py` 會擋住空泛 description：

```python
assert len(desc.group(1)) >= 30, (
    "description must be specific (>=30 chars) so the skill triggers reliably"
)
```

長度只是最低門檻，**「具體」才是真正讓它觸發的關鍵**，長度測試只是提醒你別偷懶寫一句話。

## 2. 把該交給腳本的精確活，留給 LLM 自己抓 → 結果不一致

這是 skill 設計最核心的一條，也是最常見的錯。日期、`@提及`、待辦、含單位的數字這種「該完整不漏、每次一致」的東西，如果寫在指示裡叫模型用眼睛抓，就會今天抓到 6 個數字、明天抓到 5 個。

症狀：同一份文字，跑兩次摘要，`關鍵數字` 欄位數目不一樣，或漏掉一個 `@小華`。

本範例的對策是把這部分交給 `scripts/extract.py`（純標準庫、無網路、無 API key，同輸入必同輸出）。對 `part1_adhoc/sample_input.txt` 跑出來的真實結果永遠是：

```
{
  "dates": ["2026-06-04", "2026/06/10"],
  "mentions": ["小華", "阿明"],
  "todos": ["@阿明 在 2026/06/10 前補出貨報表", "追蹤一筆 NT$12,000 的退款", "跟供應商確認下週要採購的 5 台 機器人手臂"],
  "numbers": ["320 台", "98%", "2 件", "NT$12,000", "5 台", "NT$ 250,000"]
}
```

`SKILL.md` 還明文禁止模型自己抓：

```
- Do NOT hand-extract dates / mentions / todos / numbers. Always use the script,
  so the output is consistent and nothing is missed.
```

怎麼修：把規則明確、要求精確的部分寫成腳本，在 `SKILL.md` 裡叫模型先跑腳本、再用腳本的輸出填欄位。**需要判斷的（重點摘要）留給模型，需要精確的（抽取）交給腳本。**

判斷標準很簡單：這件事「換成正則或幾行 code 就能 100% 重現」嗎？能，就寫成腳本；只有「需要理解、取捨、歸納」的才留給模型。

## 3. references 沒分離，SKILL.md 變太肥

`SKILL.md` 是每次觸發都會被讀進 context 的東西，**它要短、要像目錄**。如果把完整輸出格式範本、所有邊角規則、長範例全塞進 `SKILL.md`，每次觸發都付一次這些 token，而且模型在一大坨文字裡反而抓不到重點。

症狀：`SKILL.md` 長到要捲好幾頁；改一次輸出格式要在主檔翻半天；模型偶爾忽略夾在中段的細節規則。

本範例用 **progressive disclosure（漸進揭露）**：`SKILL.md` 只放「步驟 + 鐵則」，把真正的版面規格抽到 `references/format.md`，由 `SKILL.md` 在需要時才指它去讀：

```
3. Read `references/format.md` for the exact output layout.
```

`references/format.md` 裡才是完整的欄位順序與標題（`重點 / 待辦 / 相關日期 / 提及的人 / 關鍵數字`）。好處是：主檔輕、每次觸發便宜；格式要改只動 `references/format.md`，不碰觸發邏輯。

怎麼修：`SKILL.md` 保持精簡，把大段格式 / 範例 / 查表類資料移到 `references/`，在主檔用一句「Read `references/xxx.md`」帶過去。

## 4. SKILL.md 引用了不存在的檔案

`SKILL.md` 寫「跑 `scripts/extract.py`」「讀 `references/format.md`」，但檔案改名、搬走、或根本沒建，模型照指示去找就撲空。這種錯肉眼看 `SKILL.md` 看不出來，要靠測試擋。

`tests/test_skill_structure.py` 就是在驗這件事——frontmatter 合法，而且每個被引用的檔都真的存在：

```python
assert (SKILL_DIR / "scripts" / "extract.py").exists(), "missing scripts/extract.py"
assert (SKILL_DIR / "references" / "format.md").exists(), "missing references/format.md"
```

怎麼修：在 `SKILL.md` 裡寫到的每個 script / reference 路徑，都加進結構測試斷言。改檔名時測試先紅，你就不會把壞掉的 skill 交出去。

## 5. 腳本依賴第三方套件 / 網路 / API key

Skill 的腳本是要在使用者機器上、在對話當下被叫起來跑的。如果它 `import requests` 去打外部 API、或需要某個沒裝的套件，**換一台機器、CI、或離線就直接掛**，而且失敗訊息常常很難懂。

本範例的 `scripts/extract.py` 開宗明義：

```
Pure standard library. No network, no API key. Same input -> same output,
which is exactly why this belongs in a script and not in the prompt.
```

`pyproject.toml` 的 `dependencies = []`，CI 只跑 `uv sync` + `uv run python client_smoke_test.py`，不需要任何 secret。

怎麼修：抽取 / 轉換這類確定性腳本，盡量只用標準庫；真要第三方相依時，放進 optional extra 並在文件講清楚，別讓基本範例一裝就壞。

## 6. 沒裝 uv，或忘了先 `uv sync`

本教學用 uv 管理環境，兩個最常見的卡點：

- **沒裝 uv**：打 `uv ...` 直接 `command not found: uv`（Windows 是 `'uv' 不是內部或外部命令`）。先安裝 uv，裝完**重開終端機**讓 PATH 生效，`uv --version` 印得出版本再繼續。
- **裝了 uv 但忘了先 `uv sync`**：直接 `uv run python client_smoke_test.py` 會在沒有 `.venv` 的情況下找不到對的環境。先在 repo 根目錄跑一次 `uv sync`（它會建立 `.venv`），之後 `uv run ...` 才會在對的環境裡執行。

```
git clone https://github.com/yazelin/agent-skill-starter.git
cd agent-skill-starter
uv sync
uv run python client_smoke_test.py
```

成功的真實輸出：

```
== tests/test_skill_structure.py ==
OK: skill structure test passed

== tests/test_extract.py ==
OK: extract test passed
{"dates": ["2026-06-04", "2026/06/10"], "mentions": ["小華", "阿明"], "todos": ["@阿明 在 2026/06/10 前補出貨報表", "追蹤一筆 NT$12,000 的退款", "跟供應商確認下週要採購的 5 台 機器人手臂"], "numbers": ["320 台", "98%", "2 件", "NT$12,000", "5 台", "NT$ 250,000"]}

OK: all checks passed
```

`uv sync` / `uv run` 在 Ubuntu 與 Windows 完全相同，平台差異只在「怎麼安裝 uv」這一步。

## Debug 順序（針對 Agent Skill）

1. 先用 `uv run python client_smoke_test.py` 確認 skill 結構與抽取腳本本身正常。
2. skill 不觸發 → 先回去看 `description`，把觸發情境寫具體（坑 1）。
3. 結果不一致 → 檢查精確欄位是不是還靠模型抓，沒交給腳本（坑 2）。
4. 單獨跑 `uv run python skills/structured-summary/scripts/extract.py <檔>`，確認腳本輸出對。
5. 確認 `SKILL.md` 引到的每個檔都存在、路徑逐字正確（坑 4）。
6. `SKILL.md` 太肥 → 把格式 / 範例搬去 `references/`（坑 3）。

## 問別人前準備

- repo / branch
- 你打的完整指令與完整輸出
- `SKILL.md` 的 frontmatter（`name` + `description`）
- 你期望 skill 在什麼話術下觸發、實際有沒有觸發
- 你已經檢查過哪些設定
