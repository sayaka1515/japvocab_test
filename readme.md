# 問題紀錄

##  判定問題

有些單字解釋有分號，但判定好像沒能好好把那個分號給做處理。

---

# JapVocab - 日語單字測驗程式

JapVocab 是一款專為日語學習者設計的桌面應用程式，支援 N5 至 N1 級別單字，結合練習、考試與錯題複習功能，幫助你高效記憶日語單字。

---

## 主要功能

- **練習模式**：無時間限制，顯示單字中文意思，適合日常複習。
- **考試模式**：每題 30 秒倒數計時，結束後顯示正確率與總分。
- **錯題記錄與回顧**：自動記錄錯誤單字，並可隨時回顧。
- **間隔重複（Spaced Repetition）**：錯題將於 1 天後提醒複習，強化長期記憶。
- **多級別支援**：涵蓋 N5、N4、N3、N2、N1 單字。

---

## 系統需求

- **作業系統**：Windows
- **Python 版本**：3.9

---

## 安裝與執行

1. **安裝 Python 3.9**  
   檢查方式：

   ```sh
   python --version
   ```

   如未安裝，請至 [Python 官網](https://www.python.org/downloads/) 下載安裝。

2. **下載專案**

   ```sh
   git clone <repository-url>
   ```

3. **執行程式**
   ```sh
   cd japvocab/app
   python ui.py
   ```
   > 請確保 `output` 資料夾內有 `n1_zh.csv` ~ `n5_zh.csv`（格式：expression,reading,meaning,tags）

---

## 使用說明

1. 啟動程式（`python ui.py`）。
2. 選擇「練習模式」或「考試模式」。
3. 選擇單字級別（N5~N1）。
4. 開始測驗，輸入答案後按「提交答案」或 Enter。
5. 錯題自動記錄，可點擊「錯題回顧」查看。
6. 間隔重複會在錯題到期時提醒複習。
7. 可隨時重啟測驗或退出程式。

---

## 檔案結構

```
japvocab/
├── app/
│   ├── exam_mode.py
│   ├── practice_mode.py
│   ├── ui.py
│   └── output/
│       ├── n1_zh.csv
│       ├── n2_zh.csv
│       ├── n3_zh.csv
│       ├── n4_zh.csv
│       └── n5_zh.csv
└── wrong_answers.json（運行後自動生成）
```
