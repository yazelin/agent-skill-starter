# Agent Skill 入門模板：裝進 Claude Code

Skill 沒有「部署到雲端」這件事——它就是一個資料夾。所謂「上線」其實是「把 `skills/structured-summary/` 放到 Claude Code 看得到的 skill 目錄，讓它在對的時機自動觸發」。

## 裝之前先確認

- 已跑過 `uv sync`，且確定性測試全綠：`uv run python client_smoke_test.py` 以 `OK: all checks passed` 收尾。
- `skills/structured-summary/` 結構完整：`SKILL.md` + `scripts/extract.py` + `references/format.md` 都在。
- `SKILL.md` 的 frontmatter 有 `name` 與一段**具體**的 `description`（自動觸發靠它）。
- 抽取腳本本機跑得動：`uv run python skills/structured-summary/scripts/extract.py part1_adhoc/sample_input.txt` 吐出四欄 JSON。

## Skill 目錄在哪

Claude Code 從兩個地方找 skill：

- **使用者層級**：`~/.claude/skills/<skill-name>/`（所有專案都能用）。Windows 上是 `%USERPROFILE%\.claude\skills\<skill-name>\`。
- **專案層級**：`<你的專案>/.claude/skills/<skill-name>/`（只在那個專案裡用，可隨 repo 進版控分享給團隊）。

**重點**：被放進去的是「skill 資料夾本身」，資料夾名字（這裡是 `structured-summary`）就是 skill 名字，裡面要有 `SKILL.md`。

## 方法 1：複製進去（最直接）

把整個 skill 資料夾複製到使用者層級：

Ubuntu / macOS：

```bash
mkdir -p ~/.claude/skills
cp -r skills/structured-summary ~/.claude/skills/
```

Windows（PowerShell）：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.claude\skills"
Copy-Item -Recurse skills\structured-summary "$env:USERPROFILE\.claude\skills\"
```

複製後在那個目錄底下應該看得到 `structured-summary/SKILL.md`。缺點是：之後改 repo 裡的 skill，要記得重新複製一次。

## 方法 2：symlink（邊開發邊測，推薦）

如果你會持續改這個 skill，用 symlink 讓 `~/.claude/skills/` 指回 repo 工作樹，改一次即時生效，不用反覆複製：

Ubuntu / macOS：

```bash
mkdir -p ~/.claude/skills
ln -s "$PWD/skills/structured-summary" ~/.claude/skills/structured-summary
```

連好後 `ls -l ~/.claude/skills/` 會看到 `structured-summary -> /絕對路徑/agent-skill-starter/skills/structured-summary`。（這正是同機其他 skill 的裝法，例如 `codex-imagegen` 就是 symlink 進去的。）

Windows（PowerShell，建 symlink 需系統管理員或開啟開發者模式）：

```powershell
New-Item -ItemType SymbolicLink -Path "$env:USERPROFILE\.claude\skills\structured-summary" -Target "$PWD\skills\structured-summary"
```

> symlink 注意：因為它指回工作樹，你一改 repo 裡的 `SKILL.md` / `extract.py` 就立刻影響到 Claude Code 載到的版本。要動大改時，建議在獨立 branch / worktree 上改，避免半成品被即時載入。

## 方法 3：當成專案內 skill 隨 repo 分享

想讓團隊 clone 完就有這個 skill，把它放在專案的 `.claude/skills/` 下並進版控：

```bash
mkdir -p .claude/skills
cp -r skills/structured-summary .claude/skills/
git add .claude/skills/structured-summary
```

之後任何人在這個專案裡開 Claude Code，都能用到這個 skill，不必各自手動安裝。

## 驗證它真的被載入

裝好後開 Claude Code，用幾種方式確認：

1. **列出 skill**：在 Claude Code 裡用 skill 列表（`/` 開頭的指令清單）找 `structured-summary`，有出現代表 frontmatter 合法、目錄位置正確、已被掃到。
2. **觸發它**：丟一段符合 description 的請求，例如「幫我把這份會議記錄整理成結構化摘要」並附上 `part1_adhoc/sample_input.txt` 的內容。命中的話，Claude 會去跑 `scripts/extract.py`、讀 `references/format.md`，產出固定版面（`重點 / 待辦 / 相關日期 / 提及的人 / 關鍵數字`）的摘要。
3. **比對精確欄**：產出的 `相關日期 / 提及 / 關鍵數字` 應該跟本機直接跑 extractor 的 JSON 一致（`2026-06-04`、`2026/06/10`、`小華`、`阿明`、`320 台`、`98%`、`NT$12,000`、`NT$ 250,000` 等）。一致，就代表「精確的部分交給腳本」這條真的接上了。

## 沒被觸發？先查這幾項

- **description 太籠統**：模型靠 description 判斷何時用。太空泛（例如只寫「整理文字」）就不會命中。把觸發情境寫具體（`Use when ...` + meeting minutes / work logs / messy notes）。
- **目錄放錯層**：確認 skill 資料夾在 `~/.claude/skills/<name>/` 或 `<專案>/.claude/skills/<name>/`，且裡面有 `SKILL.md`。
- **frontmatter 壞掉**：`---` 沒成對、缺 `name` 或 `description`，整個 skill 會被忽略。先在 repo 跑 `uv run python tests/test_skill_structure.py`，綠了才代表結構合法。
- **改完沒生效**：用方法 1（複製）的話，記得重新複製；symlink 則會自動跟著最新檔。

## 上線前實務提醒

- skill 裡的腳本會在你的機器上實際執行。確認它（像 `extract.py` 一樣）零相依、無網路、不碰機密，會降低風險。
- description 是「自動觸發契約」，改它等於改觸發行為——改完最好實際丟幾個請求驗一次有沒有過度/不足觸發。
- 把 skill 進版控（方法 3）時，連同 `tests/` 一起進，CI 才能在每次改動後守住「結構合法 + 抽取正確」。

## 延伸資源

想看更多真實 skill 怎麼寫：

- 官方 skills：https://github.com/anthropics/skills
- 社群 superpowers：https://github.com/obra/superpowers
