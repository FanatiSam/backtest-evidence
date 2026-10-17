# Backtest Evidence

一套小型、可檢查的回測證據工具。Python 3.10 以上即可執行，無執行期第三方套件、券商連線或 API key 需求。

這是從私人量化研究流程經驗整理出的**全新獨立實作**。目前是早期版本，尚未建立外部使用或獨立審查紀錄；所有範例都是合成資料。

0.1.1 候選版已做維護者內部實際試用：兩份歷史輸出、五條序列；其中四條揭露日曆合併產生的空白，一條完整序列通過獨立算術實作核對。這不是外部審查，也沒有公開私人績效。

候選版位於 `trial-and-case-studies` 分支，等待維護者檢視。參閱 [10 分鐘試用指南](docs/TRY_IT.md)、[合成案例](docs/CASE_STUDIES.md) 和 [試用紀錄](docs/TRIAL_REPORT.md)。

## 快速開始

```bash
git clone https://github.com/FanatiSam/backtest-evidence.git
cd backtest-evidence
python3 -m backtest_evidence report examples/daily_pnl.csv --capital 1000 --sessions examples/sessions.csv
python3 -m unittest discover -s tests -v
```

## 主要功能

不同欄位名稱可以用 `--date-column` 和 `--pnl-column` 明確指定。多策略表格一次只讀選定的一條序列，不自動加總、補零或刪除日期。

- **PnL 報告**：淨損益、權益、最大回撤、PnL／最大回撤及零無風險利率 Sharpe；最大回撤包含初始資金基準。
- **缺值檢查**：缺值不當作零；缺值或遺漏交易日時，暫不產生績效指標。遺漏日期需要另外提供預期交易日清單才能辨識。
- **時間檢查**：資料可用時間 ≤ 決策時間 ≤ 執行時間。必須明確提供時區；無法驗證時間戳本身是否真實。
- **研究日期檢查**：檢查提供的觀測日期有沒有進入 OOS。這不是檔案存取防火牆，也不證明以前沒有看過 OOS。
- **檔案指紋**：針對明確指定的檔案產生及驗證 SHA-256 清單；不自動收集整個資料夾。

輸入必須是扣除成本、包含未平倉市值變動的每日淨 PnL，且期間沒有入金或出金。零 PnL 不等於沒有交易。

範例五天淨利 100、最大回撤 50，僅用於展示計算，不代表策略績效。檢查通過也不代表策略有效、可交易或值得投資。

完整欄位、命令、限制與方法請見 [英文 README](README.md) 和 [方法文件](docs/METHODOLOGY.md)。
