---
name: ibonCustomerAnalysisSkill
description: 分析 ibon 客群組成與行為特徵的 Skill
---

# ibon 客群分析 Skill (ibonCustomerAnalysisSkill)

此 Skill 專門用來分析 ibon 的客群交易資料 (`/api/v1/ibonUserInfo`) 與門市資訊 (`/api/v1/StoreDesc`)，以了解各門市或整體的年齡、性別與情緒分佈等特徵。

> [!IMPORTANT]
> **AI AGENT INSTRUCTION:**
> **使用此 Skill 前，必須先向使用者確認目標 API 的 IP 位址，並驗證 API 資訊！**
> 1. 預設的 `127.0.0.1` 只是範例，實際連線的 IP 是可以變動的。如果使用者沒有主動提供 IP，你必須停止並詢問使用者：「請問這次要查詢的 API IP 位址為何？（例如 127.0.0.1）」。
> 2. 確認 IP 後，必須先存取 `http://<IP>:9846/openapi.json`，並驗證以下資訊：
>    - 抬頭 (title) 必須為 `"ibon Data Access API for AI"`。
>    - 中介層資料庫 API 版號 (version) 必須與目前的 Skill 相符 (目前此 Skill 對應的版本為 `1.0312.115`)。
>    **若不符合，請提醒使用者並停止使用此 Skill。**
> 3. 確認無誤後，再執行腳本進行查詢，帶入 `--host <IP>` 參數。

## 目錄結構
- `SKILL.md`: Skill 的說明與 AI 助理提示。
- `scripts/analyze.py`: Python 分析腳本，處理資料抓取與轉換。
- `scripts/requirements.txt`: 腳本所需執行的 Python 套件。

## 執行方式
```bash
pip install -r scripts/requirements.txt
python scripts/analyze.py --host <IP>
```
