import random
import csv
import re
import os
import requests
import threading

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

# 從 Tatoeba API 抓取例句（非同步）
def get_tatoeba_examples(word, callback):
    url = f"https://tatoeba.org/api/v2/search?query={requests.utils.quote(word)}&from=jpn&to=eng"
    try:
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
        examples = []
        for sentence in data.get("sentences", []):
            if "jpn" in sentence and "eng" in sentence:
                jp_text = sentence["jpn"]["text"]
                en_text = sentence["eng"]["text"]
                examples.append((jp_text, en_text))
                if len(examples) >= 2:
                    break
        callback(examples if examples else None)
    except requests.exceptions.RequestException as e:
        print(f"Error fetching from Tatoeba: {e}")
        callback(None)

class PracticeMode:
    def __init__(self, ui_instance):
        print("初始化 PracticeMode...")  # 調試輸出
        self.vocab = []
        self.current_word = None
        self.score = 0
        self.ui = ui_instance
        self.example_fetching = False
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
        except FileNotFoundError:
            print(f"錯誤：找不到 {file_path}")  # 調試輸出
            self.ui.update_result(f"錯誤：找不到 {file_path}。請確保 output 資料夾中存在該檔案！")
            self.ui.root.quit()

    def get_current_word_display(self):
        return f"日文: {self.current_word['jp']} ({self.current_word['kana']})" if self.current_word else "日文: 無單字"

    def next_word(self):
        if not self.vocab:
            self.ui.update_result("詞彙表為空！請檢查檔案內容。\n")
            return
        self.current_word = random.choice(self.vocab)
        self.ui.update_word()
        self.example_fetching = False

    def check_answer(self, answer):
        if self.example_fetching or not self.current_word:
            return
        cleaned_answer = clean_answer(answer)
        possible_meanings = get_possible_meanings(self.current_word['zh'])
        if cleaned_answer in possible_meanings:
            self.score += 10
            self.is_correct = True
        else:
            self.is_correct = False
        self.example_fetching = True
        threading.Thread(target=lambda: get_tatoeba_examples(self.current_word['jp'], self.update_examples), daemon=True).start()

    def update_examples(self, examples):
        if self.current_word:
            if self.is_correct:
                msg = f"正確！+10分\n答案包含：{self.current_word['zh']}\n"
            else:
                msg = f"錯了！正確答案: {self.current_word['zh']}\n"
            if examples:
                example_str = "\n".join([f"{jp} - {en}" for jp, en in examples])
            else:
                example_str = "請用 Jisho.org 查例句！(Tatoeba 無例句或網路問題)"
            self.ui.update_result(f"{msg}例句:\n{example_str}\n")
        self.example_fetching = False
        self.next_word()

    def reset_quiz(self):
        self.score = 0
        self.next_word()
        self.ui.update_result("測驗已重啟！\n")