import tkinter as tk
from tkinter import messagebox, scrolledtext
from practice_mode import PracticeMode
from exam_mode import ExamMode
import json
import os
from datetime import datetime, timedelta

class UIApp:
    def __init__(self, root):
        print("初始化 UIApp...")  # 調試輸出
        self.root = root
        self.root.title("日語單字測驗")
        self.root.geometry("600x500")
        self.mode = tk.StringVar(value="練習模式")
        self.level = tk.StringVar(value="N5")
        self.quiz = None

        # 模式和級別選擇
        tk.Label(root, text="選擇模式：", font=("Arial", 12)).pack(pady=5)
        modes = ["練習模式", "考試模式"]
        tk.OptionMenu(root, self.mode, *modes, command=self.on_mode_change).pack(pady=5)

        tk.Label(root, text="選擇測驗級別：", font=("Arial", 12)).pack(pady=5)
        levels = ["N5", "N4", "N3", "N2", "N1"]
        tk.OptionMenu(root, self.level, *levels).pack(pady=5)

        self.score_label = tk.Label(root, text="分數: 0", font=("Arial", 12))
        self.score_label.pack(pady=5)

        self.word_label = tk.Label(root, text="日文: 請選擇模式開始測驗", font=("Arial", 14))
        self.word_label.pack(pady=10)

        tk.Label(root, text="你的答案:", font=("Arial", 12)).pack()
        self.answer_entry = tk.Entry(root, font=("Arial", 12), width=30)
        self.answer_entry.pack(pady=5)
        self.answer_entry.bind("<Return>", lambda event: self.on_submit())

        tk.Button(root, text="提交答案", command=self.on_submit, font=("Arial", 12)).pack(pady=5)
        tk.Button(root, text="重啟測驗", command=self.on_reset, font=("Arial", 12)).pack(pady=5)
        tk.Button(root, text="錯題回顧", command=self.review_wrong_answers, font=("Arial", 12)).pack(pady=5)
        tk.Button(root, text="退出", command=self.on_quit, font=("Arial", 12)).pack(pady=5)

        self.result_text = scrolledtext.ScrolledText(root, height=10, width=60, font=("Arial", 12), wrap=tk.WORD)
        self.result_text.pack(pady=10)
        self.result_text.config(state='disabled')

        print("檢查間隔重複...")  # 調試輸出
        self.check_spaced_repetition()  # 啟動時檢查是否需要複習
        print("開始載入模式...")  # 調試輸出
        self.on_mode_change(self.mode.get())  # 初始載入練習模式

    def check_spaced_repetition(self):
        if not os.path.exists("wrong_answers.json"):
            return
        with open("wrong_answers.json", "r", encoding="utf-8") as f:
            wrong_answers = json.load(f)
        current_time = datetime.now()
        for item in wrong_answers:
            if "next_review" in item and datetime.fromisoformat(item["next_review"]) <= current_time:
                messagebox.showinfo("間隔重複複習", f"該複習了！\n日文: {item['question']} ({item['reading']})\n正確答案: {item['correct_answer']}")

    def on_mode_change(self, mode):
        print(f"切換模式: {mode}")  # 調試輸出
        level = self.level.get()
        if mode == "練習模式":
            self.quiz = PracticeMode(self)
        elif mode == "考試模式":
            self.quiz = ExamMode(self)
        self.quiz.load_vocab(level)
        self.update_score()
        self.update_word()
        self.update_result("")  # 初始化時清空結果，避免顯示預設訊息

    def on_submit(self):
        answer = self.answer_entry.get().strip()
        if answer:
            self.quiz.check_answer(answer)
            self.update_score()
        else:
            self.update_result("請輸入答案！\n")

    def on_reset(self):
        level = self.level.get()
        self.quiz.load_vocab(level)
        self.update_result("")
        self.update_score()
        self.update_word()

    def review_wrong_answers(self):
        if not os.path.exists("wrong_answers.json"):
            messagebox.showinfo("提示", "目前沒有錯題記錄！")
            return
        with open("wrong_answers.json", "r", encoding="utf-8") as f:
            wrong_answers = json.load(f)
        if not wrong_answers:
            messagebox.showinfo("提示", "目前沒有錯題記錄！")
            return
        review_text = "錯題回顧：\n"
        for item in wrong_answers:
            review_text += f"日文: {item['question']} ({item['reading']})\n你的答案: {item['answer']}\n正確答案: {item['correct_answer']}\n\n"
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, review_text)
        self.result_text.config(state='disabled')

    def on_quit(self):
        messagebox.showinfo("結束", f"遊戲結束！最終分數: {self.quiz.score if self.quiz else 0}")
        self.root.quit()

    def update_word(self):
        word_text = self.quiz.get_current_word_display() if self.quiz and self.quiz.current_word else "日文: 請選擇模式開始測驗"
        self.word_label.config(text=word_text)

    def update_score(self):
        score_text = f"分數: {self.quiz.score if self.quiz else 0}"
        self.score_label.config(text=score_text)

    def update_result(self, result_text=""):
        self.result_text.config(state='normal')
        self.result_text.delete(1.0, tk.END)
        self.result_text.insert(tk.END, result_text)
        self.result_text.config(state='disabled')

if __name__ == "__main__":
    print("啟動程式...")  # 調試輸出
    root = tk.Tk()
    app = UIApp(root)
    print("進入主迴圈...")  # 調試輸出
    root.mainloop()
    print("程式結束")  # 調試輸出