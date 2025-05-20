# 使用 Python 基礎映像
FROM python:3.10

# 設定工作目錄
WORKDIR /app

# 複製專案檔案
COPY . .

# 安裝依賴
RUN pip install -r requirements.txt

# 指定執行指令
CMD ["python", "app.py"]
