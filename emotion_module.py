from utils import safe_generate

# 使用 Gemini 判斷輸入語句的情緒（快樂、悲傷、生氣、中性）
def detect_emotion(text):
    prompt = f"""
你是一個情緒分析助手，請從以下句子中判斷使用者的情緒，並只回覆「快樂」、「悲傷」、「生氣」或「中性」其中一種，不要加任何其他文字。

句子：「{text}」
"""
    emotion = safe_generate(prompt)
    if emotion not in ["快樂", "悲傷", "生氣", "中性"]:
        return "中性"
    return emotion
