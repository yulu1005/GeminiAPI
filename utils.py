import time
import json
from datetime import datetime
import google.generativeai as genai

# 初始化 Gemini Flash 模型
genai.configure(api_key="AIzaSyCbb7CY1YhUH2s88srRbkQkIoy2m1owRew")
model = genai.GenerativeModel("gemini-2.0-flash")

# 安全呼叫 Gemini

def safe_generate(prompt):
    try:
        return model.generate_content(prompt).text.strip()
    except Exception as e:
        if "429" in str(e):
            print("⚠️ 達到API限制，等待60秒後重試...")
            time.sleep(60)
            try:
                return model.generate_content(prompt).text.strip()
            except Exception as e2:
                print("再次失敗：", e2)
                return None
        else:
            print("呼叫錯誤：", e)
            return None

# 通用 JSON 讀取函式
def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except:
        return []

# 通用 JSON 寫入函式
def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

# ✅ 儲存聊天紀錄
def save_chat_log(user_input, ai_response):
    log = {
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "user": user_input,
        "response": ai_response
    }
    try:
        with open("chat_history.json", "r", encoding="utf-8") as f:
            records = json.load(f)
    except:
        records = []

    records.append(log)
    with open("chat_history.json", "w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)
