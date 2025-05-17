import random
import csv
import re
import tkinter as tk
from tkinter import messagebox, scrolledtext
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

class VocabQuizApp:
    def __init__(self, root):
        self.root = root
        self.root.title("日語單字測驗 (N5-N1)")
        self.root.geometry("600x500")

        # 變數初始化
        self.vocab = []
        self.current_word = None
        self.score = 0
        self.level = tk.StringVar(value="N5")
        self.example_fetching = False
        self.is_correct = False  # 記錄答題是否正確

        # GUI 元素
        tk.Label(root, text="選擇測驗級別：", font=("Arial", 12)).pack(pady=5)
        levels = ["N5", "N4", "N3", "N2", "N1"]
        tk.OptionMenu(root, self.level, *levels, command=self.load_vocab).pack(pady=5)

        self.score_label = tk.Label(root, text=f"分數: {self.score}", font=("Arial", 12))
        self.score_label.pack(pady=5)

        self.word_label = tk.Label(root, text="日文: 請選擇級別開始測驗", font=("Arial", 14))
        self.word_label.pack(pady=10)

        tk.Label(root, text="你的答案:", font=("Arial", 12)).pack()
        self.answer_entry = tk.Entry(root, font=("Arial", 12), width=30)
        self.answer_entry.pack(pady=5)
        self.answer_entry.bind("<Return>", lambda event: self.check_answer())

        tk.Button(root, text="提交答案", command=self.check_answer, font=("Arial", 12)).pack(pady=5)
        tk.Button(root, text="重啟測驗", command=self.reset_quiz, font=("Arial", 12)).pack(pady=5)
        tk.Button(root, text="退出", command=self.quit_app, font=("Arial", 12)).pack(pady=5)

        self.result_text = scrolledtext.ScrolledText(root, height=10, width=60, font=("Arial", 12), wrap=tk.WORD)
        self.result_text.pack(pady=10)
        self.result_text.config(state='disabled')

        self.load_vocab(self.level.get())

    def load_vocab(self, level):
        file_path = os.path.join("output", f"{level.lower()}_zh.csv")
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
            self.score = 0
            self.score_label.config(text=f"分數: {self.score}")
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, f"已載入 {level} 詞彙表！\n")
            self.result_text.config(state='disabled')
            self.next_word()
        except FileNotFoundError:
            messagebox.showerror("錯誤", f"找不到 {file_path}。請確保 output 資料夾中存在該檔案！")
            self.root.quit()

    def next_word(self):
        if not self.vocab:
            self.result_text.config(state='normal')
            self.result_text.delete(1.0, tk.END)
            self.result_text.insert(tk.END, "詞彙表為空！請檢查檔案內容。\n")
            self.result_text.config(state='disabled')
            return

        self.current_word = random.choice(self.vocab)
        self.word_label.config(text=f"日文: {self.current_word['jp']} ({self.current_word['kana']})")
        self.answer_entry.delete(0, tk.END)
        self.answer_entry.focus()
        self.example_fetching = False

    def check_answer(self):
        if not self.current_word or self.example_fetching:
            return

        answer = self.answer_entry.get().strip()
        if not answer:
            return

        cleaned_answer = clean_answer(answer)
        possible_meanings = get_possible_meanings(self.current_word['zh'])

        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)

        if cleaned_answer in possible_meanings:
            self.score += 10
            self.is_correct = True
            self.result_text.insert(tk.END, f"正確！+10分\n答案包含：{self.current_word['zh']}\n")
        else:
            self.is_correct = False
            self.result_text.insert(tk.END, f"錯了！正確答案: {self.current_word['zh']}\n")

        self.score_label.config(text=f"分數: {self.score}")
        self.result_text.config(state='disabled')
        
        # 無論對錯都抓取例句
        self.example_fetching = True
        threading.Thread(target=lambda: get_tatoeba_examples(self.current_word['jp'], self.update_examples), daemon=True).start()

    def update_examples(self, examples):
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        if self.current_word:
            if self.is_correct:
                msg = f"正確！+10分\n答案包含：{self.current_word['zh']}\n"
            else:
                msg = f"錯了！正確答案: {self.current_word['zh']}\n"
            if examples:
                example_str = "\n".join([f"{jp} - {en}" for jp, en in examples])
            else:
                example_str = "請用 Jisho.org 查例句！(Tatoeba 無例句或網路問題)"
            self.result_text.insert(tk.END, f"{msg}例句:\n{example_str}\n")
        self.result_text.config(state='disabled')
        self.example_fetching = False
        # 例句顯示完成後再切換到下一題
        self.next_word()

    def reset_quiz(self):
        self.score = 0
        self.score_label.config(text=f"分數: {self.score}")
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, "測驗已重啟！\n")
        self.result_text.config(state='disabled')
        self.next_word()

    def quit_app(self):
        messagebox.showinfo("結束", f"遊戲結束！最終分數: {self.score}")
        self.root.quit()

if __name__ == "__main__":
    root = tk.Tk()
    app = VocabQuizApp(root)
    root.mainloop()