from emotion_module import detect_emotion
from utils import safe_generate, save_chat_log, load_json
from datetime import datetime

def chat_response(text):
    # 讀取最近三筆聊天紀錄
    history = load_json("chat_history.json")[-3:]
    context = "\n".join([f"使用者：{h['user']}\nAI：{h['response']}" for h in history])

    # 判斷語氣
    emotion = detect_emotion(text)
    tone_map = {
        "快樂": "用開朗活潑的語氣",
        "悲傷": "用溫柔安慰的語氣",
        "生氣": "用穩定理性的語氣",
        "中性": "自然地"
    }
    tone = tone_map.get(emotion, "自然地")

    # 包含上下文的 prompt
    prompt = f"""{context}
使用者：{text}
請以{tone}語氣回應使用者，只能使用中文："""

    reply = safe_generate(prompt)
    save_chat_log(text, reply)
    return reply


# 主動問候語產生（依時段）
def generate_greeting():
    now = datetime.now().hour
    if now < 11:
        return safe_generate("請用溫柔語氣說早安並問今天打算做什麼")
    elif now < 14:
        return safe_generate("請用輕鬆語氣說午安並關心午餐情況")
    elif now < 19:
        return safe_generate("請用自然語氣說下午好並問今天過得如何")
    else:
        return safe_generate("請用放鬆語氣說晚上好並詢問今天有沒有累")
