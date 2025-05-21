# voice_main.py
import os
import whisper
import sounddevice as sd
import soundfile as sf
import asyncio
import edge_tts

from main import classify_intent
from item_module import handle_item_input, query_item_by_keyword
from schedule_module import handle_schedule_input, query_schedule
from chat_module import chat_response

# ==== 設定參數 ====
DURATION = 5
SAMPLE_RATE = 44100
CHANNELS = 1
INPUT_DEVICE = 6  # 請依 sd.query_devices() 結果調整
WAV_FILE = "audio.wav"
OUTPUT_MP3 = "output.mp3"
VOICE = "zh-TW-HsiaoChenNeural"

# ==== 錄音 ====
def record_audio():
    sd.default.device = (INPUT_DEVICE, None)
    print("錄音中，請說話...")
    audio = sd.rec(int(DURATION * SAMPLE_RATE), samplerate=SAMPLE_RATE, channels=CHANNELS)
    sd.wait()
    sf.write(WAV_FILE, audio, SAMPLE_RATE)
    print("錄音完成！")

# ==== Whisper 語音辨識 ====
def transcribe_audio():
    model = whisper.load_model("base")
    result = model.transcribe(WAV_FILE)
    return result['text']

# ==== 播放語音（僅儲存 mp3，讓主機播放） ====
async def speak(text):
    communicate = edge_tts.Communicate(text=text, voice=VOICE)
    await communicate.save(OUTPUT_MP3)
    print(f"語音儲存為 {OUTPUT_MP3}，請在主機播放")

# ==== 任務派遣 ====
def handle_text(text):
    task_type = classify_intent(text)
    print("分類結果：", task_type)

    if task_type == "記錄物品":
        return handle_item_input(text)
    elif task_type == "安排時程":
        return handle_schedule_input(text)
    elif task_type == "聊天":
        return chat_response(text)
    else:
        return "我還不太懂你要我做什麼。"

# ==== 主流程 ====
if __name__ == "__main__":
    record_audio()
    user_text = transcribe_audio()
    print("Whisper 辨識：", user_text)

    reply = handle_text(user_text)
    print("AI 回應：", reply)

    asyncio.run(speak(reply))
