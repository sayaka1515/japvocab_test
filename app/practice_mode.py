import random
import csv
import re
import os
import json
from datetime import datetime, timedelta

# 清理答案函數，移除多餘字符並正規化（僅用於比較）
def clean_answer(text):
    text = re.sub(r'\s+', '', text)
    return text.lower().strip()

# 提取所有可能的意思，包括括號內的詞彙
def get_possible_meanings(zh_text):
    meanings = []
    paren_contents = re.findall(r'\((.*?)\)', zh_text)
    main_text = re.sub(r'\([^)]*\)', '', zh_text)
    meanings.extend(re.split(r'[，；]', main_text))
    for content in paren_contents:
        meanings.extend(re.split(r'[，]', content))
    meanings = [clean_answer(m) for m in meanings if m.strip()]
    return meanings

def save_wrong_answer(question, reading, user_answer, correct_answer):
    wrong_answer = {
        "question": question,
        "reading": reading,
        "answer": user_answer,
        "correct_answer": correct_answer,
        "next_review": (datetime.now() + timedelta(days=1)).isoformat(),
        "review_interval": 1  # 初始間隔 1 天
    }
    if not os.path.exists("wrong_answers.json"):
        with open("wrong_answers.json", "w", encoding="utf-8") as f:
            json.dump([], f)
    with open("wrong_answers.json", "r", encoding="utf-8") as f:
        wrong_answers = json.load(f)
    wrong_answers.append(wrong_answer)
    with open("wrong_answers.json", "w", encoding="utf-8") as f:
        json.dump(wrong_answers, f)

class PracticeMode:
    def __init__(self, ui_instance):
        print("初始化 PracticeMode...")  # 調試輸出
        self.vocab = []
        self.current_word = None
        self.score = 0
        self.ui = ui_instance
        self.is_correct = False

    def load_vocab(self, level):
        file_path = os.path.join(os.path.dirname(__file__), "output", f"{level.lower()}_zh.csv")
        print(f"嘗試載入檔案: {file_path}")  # 調試輸出
        self.vocab = []
        try:
            with open(file_path, "r", encoding="utf-8") as file:
                reader = csv.DictReader(file)
                for row in reader:
                    if row["expression"] and row["reading"] and row["meaning"]:
                        self.vocab.append({
                            "jp": row["expression"],
                            "kana": row["reading"],
                            "zh": row["meaning"],
                            "tags": row["tags"]
                        })
            print(f"成功載入 {len(self.vocab)} 個詞彙")  # 調試輸出
            self.score = 0
            self.ui.update_result(f"已載入 {level} 詞彙表！\n")
            self.next_word()  # 自動進入第一題
        except FileNotFoundError as e:
            print(f"錯誤：找不到 {file_path} - {e}")  # 調試輸出
            self.ui.update_result(f"錯誤：找不到 {file_path}。請確保 output 資料夾中存在該檔案！")
            self.ui.root.quit()
        except Exception as e:
            print(f"載入失敗: {e}")  # 調試輸出
            self.ui.update_result(f"載入失敗: {e}")

    def get_current_word_display(self):
        return f"日文: {self.current_word['jp']} ({self.current_word['kana']})" if self.current_word else "日文: 無單字"

    def next_word(self):
        if not self.vocab:
            self.ui.update_result("詞彙表為空！請檢查檔案內容。\n")
            return
        self.current_word = random.choice(self.vocab)
        self.ui.update_word()

    def check_answer(self, answer):
        if not self.current_word:
            return
        cleaned_answer = clean_answer(answer)
        possible_meanings = get_possible_meanings(self.current_word['zh'])
        if cleaned_answer in possible_meanings:
            self.score += 10
            self.is_correct = True
            msg = f"正確！+10分\n答案包含：{self.current_word['zh']}\n"
        else:
            self.is_correct = False
            save_wrong_answer(self.current_word['jp'], self.current_word['kana'], answer, self.current_word['zh'])
            msg = f"錯了！正確答案: {self.current_word['zh']}\n"
        self.ui.update_result(msg)
        self.next_word()

    def reset_quiz(self):
        self.score = 0
        self.next_word()
        self.ui.update_result("測驗已重啟！\n")