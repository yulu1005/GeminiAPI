import schedule
import time
from item_module import handle_item_input, query_item_by_keyword, delete_item_by_keyword
from schedule_module import handle_schedule_input, query_schedule, delete_schedule_by_keyword
from chat_module import chat_response, generate_greeting
from utils import safe_generate

# 語意分類：判斷語句是物品 / 時程 / 聊天

def classify_intent(text):
    prompt = f"""
請根據句子判斷使用者想做什麼動作，只回傳以下其中一項（不得自由發揮）：

- 記錄物品：如果是想記住東西放在哪裡
- 安排時程：如果是提醒自己某天要做什麼事
- 聊天：如果只是隨便說說或敘述心情
- 查詢物品、刪除物品、查詢時程、刪除時程：如有明確詢問或取消的語句才使用

範例：
「幫我記得我把耳機放在抽屜」→ 記錄物品
「我明天下午要去打針」→ 安排時程
「我今天好累喔」→ 聊天

請判斷句子：「{text}」
只回傳：「記錄物品」、「安排時程」、「聊天」、「查詢物品」、「刪除物品」、「查詢時程」、「刪除時程」其中之一。
"""
    return safe_generate(prompt)

# 主動問候觸發函式

def morning_greet():
    print("早安：")
    print(generate_greeting())

def noon_greet():
    print("午安：")
    print(generate_greeting())

def evening_greet():
    print("晚安：")
    print(generate_greeting())

# 註冊定時排程（每天固定時間問候）
schedule.every().day.at("09:00").do(morning_greet)
schedule.every().day.at("12:00").do(noon_greet)
schedule.every().day.at("17:00").do(evening_greet)

# 主程式

def main():
    while True:
        schedule.run_pending()  # 執行排程
        text = input("使用者：")

        if text.lower() in ["q", "exit"]:
            break

        intent = classify_intent(text)

        if "記錄物品" in intent:
            handle_item_input(text)
            reply = chat_response("我剛剛幫你記錄了一項物品")
            print("Gemini：", reply)

        elif "安排時程" in intent:
            handle_schedule_input(text)
            reply = chat_response("我剛剛幫你安排了一個時程")
            print("Gemini：", reply)

        elif "查詢物品" in intent:
            query_item_by_keyword(text)

        elif "刪除物品" in intent:
            delete_item_by_keyword(text)

        elif "查詢時程" in intent:
            query_schedule(keyword=text)

        elif "刪除時程" in intent:
            delete_schedule_by_keyword(text)

        else:
            reply = chat_response(text)
            print("Gemini：", reply)

        time.sleep(1)

if __name__ == "__main__":
    main()
