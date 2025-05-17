import csv
import time
from deep_translator import GoogleTranslator
import requests

# 初始化翻譯器（英文到繁體中文）
translator = GoogleTranslator(source='en', target='zh-TW')

# 檔案路徑
input_file = "C:\\Users\\Yukari17\\Downloads\\japanese\\n1.csv"
output_file = "C:\\Users\\Yukari17\\Downloads\\japanese\\n1_zh.csv"
translated_rows = []

# 讀取 n5.csv
try:
    with open(input_file, "r", encoding="utf-8") as file:
        reader = csv.DictReader(file)
        fieldnames = reader.fieldnames  # 保留欄位
        rows = list(reader)  # 將所有行讀入記憶體
        total_rows = len(rows)

        print(f"共 {total_rows} 行待翻譯...")
        
        # 批量處理，每 10 行翻譯一次
        batch_size = 10
        for i in range(0, total_rows, batch_size):
            batch = rows[i:i + batch_size]
            print(f"處理第 {i+1} 至 {min(i+batch_size, total_rows)} 行...")

            for row in batch:
                if row["meaning"]:  # 確保 meaning 不為空
                    retries = 3
                    while retries > 0:
                        try:
                            # 翻譯英文到中文，設置超時
                            zh_meaning = translator.translate(row["meaning"])
                            new_row = row.copy()
                            new_row["meaning"] = zh_meaning
                            translated_rows.append(new_row)
                            break
                        except (requests.exceptions.RequestException, Exception) as e:
                            print(f"翻譯 '{row['meaning']}' 失敗，重試...（剩餘 {retries-1} 次）")
                            retries -= 1
                            time.sleep(2)  # 等待 2 秒後重試
                        if retries == 0:
                            print(f"翻譯 '{row['meaning']}' 失敗，保留英文")
                            translated_rows.append(row)  # 失敗保留原文
                else:
                    translated_rows.append(row)  # 空 meaning 保留

            time.sleep(1)  # 每批次間隔 1 秒，降低 API 壓力

    # 寫入 n5_zh.csv
    with open(output_file, "w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(translated_rows)

    print(f"翻譯完成！新檔案已保存為 {output_file}")

except FileNotFoundError:
    print(f"錯誤：找不到 {input_file}。請確認檔案存在。")
except Exception as e:
    print(f"發生錯誤：{e}")