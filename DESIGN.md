# Agent Skill 入門模板 CI Design

> English name: Agent Skill Starter

## 定位

**主要受眾：** 想把自己一套重複做法打包成 Claude Code Skill 的開發者。
**核心承諾：** 用一個最小但完整的 skill，看懂 frontmatter 自動觸發、確定性腳本、progressive disclosure。
**痛點切入：** 不是「會不會寫 prompt」，而是讓一套做法寫一次、自動觸發，且精確的部分每次都一致。
**類別提示：** SKILL.md / frontmatter / progressive disclosure

## 視覺識別

- **主色：** `#2dd4bf`（teal）
- **輔色：** `#0d9488`
- **背景：** `#06140f`
- **語言策略：** 繁體中文為主，英文產品名作為輔助與 SEO。
- **風格：** dark developer-tool landing page、技術網格、code-card hero、高對比 CTA。

## 設計理念

### 為什麼一個 skill 要這樣切

這個模板的整套設計都在示範同一句話：**需要判斷的留給模型，需要精確的交給腳本。**

以 `structured-summary`（把雜亂筆記整理成固定格式摘要）為例：

- `重點`（3-5 條）需要理解上下文、取捨輕重 -> 這是模型擅長、也只有模型能做好的，交給模型自己讀完歸納。
- `待辦 / 相關日期 / 提及 / 關鍵數字` 的共同特徵是「該完整不漏、每次一致」。讓模型用眼睛去抓，就會偶爾漏一個日期、看錯一個金額，而且同一份輸入今天明天結果不同。這種活交給 `scripts/extract.py` 用正則確定性抽取，同輸入永遠同輸出。

把這兩種職責混在一起（全丟給模型，或全寫死成腳本）都會壞：全丟模型 -> 不穩；全寫死 -> 失去判斷力。skill 的價值就在於明確劃這條線。

### 為什麼分 Part 1 / Part 2

直接給人一個寫好的 skill，看不出它解決了什麼。所以模板先用 Part 1（`part1_adhoc/`）重現「沒有 skill」的真實痛點 —— 每次重貼一長串 prompt、結果不一致、精確欄位靠模型眼睛抓、不會自動觸發 —— 再用 Part 2 把同一個任務打包成 skill。讀者是在「修好一個自己感受過的痛」，而不是憑空背 skill 結構。

### SKILL.md 與 progressive disclosure

`SKILL.md` 的 YAML frontmatter（`name` + 一段夠具體的 `description`）是 skill 能不能被模型挑中、自動觸發的關鍵；description 越能描述「什麼情境該用」，觸發越可靠。

格式細節不寫進 `SKILL.md` 本體，而是放到 `references/format.md`，由 `SKILL.md` 在需要時才指向它。這就是 progressive disclosure：主檔保持精簡好觸發，細節按需載入，不一次塞爆 context。

### 確定性測試策略

skill 的一半價值是「自動觸發」，但「模型有沒有正確觸發 skill」需要真模型才能驗，不適合放進每次都要綠的 CI。所以測試只鎖確定性、免 key、不連網的部分：

- `tests/test_skill_structure.py` — 驗 frontmatter 合法（`name` + 夠長的 `description`）、被引用的檔案（`scripts/extract.py`、`references/format.md`）真的存在。這保證 skill 結構是「可被發現、不會引到不存在的檔」。
- `tests/test_extract.py` — 實際跑抽取器對樣本，斷言抽到的欄位。因為抽取器是純函式、確定性，這個斷言可重複。
- `client_smoke_test.py` — 串起上面兩個，CI 只跑這一支。

劃法和上面同一條線：能精確驗的（結構、抽取）寫成自動測試；需要判斷的（觸發品質、`重點` 寫得好不好）留給人。

## Landing Page CTA

主要 CTA：**收到更新 / 小班開課通知**
表單區塊以 `id="waitlist"` 為錨點，目前放 MailerLite placeholder（`data-form="REPLACE_WITH_MAILERLITE_FORM_ID"`，待手動接上真實 form id），並附 fallback 來信 `yaze.lin.j303@gmail.com`。

## 功能賣點

- Part 1 ad-hoc baseline 重現「沒有 skill」的痛
- Part 2 把同一套做法打包成自動觸發的 skill
- SKILL.md frontmatter（name / description）驅動自動觸發
- scripts/extract.py 確定性抽取 dates / mentions / todos / numbers
- references/format.md 用 progressive disclosure 載入輸出格式
- 免 key 確定性測試：驗結構 + 跑抽取斷言，CI 一鍵綠

## Assets

- `index.html`：繁中 GitHub Pages CTA landing page（teal 深色系，code-card hero）
