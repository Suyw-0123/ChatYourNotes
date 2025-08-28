# 使用 Python 3.11 作為基礎映像檔
FROM python:3.11-slim

# 設定工作目錄
WORKDIR /app

# 安裝系統依賴（Tesseract OCR 和 Poppler）
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-chi-tra \
    poppler-utils \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# 複製 requirements 文件
COPY requirements.txt .

# 安裝 Python 依賴
RUN pip install --no-cache-dir -r requirements.txt

# 複製專案文件
COPY . .

# 創建必要的目錄
RUN mkdir -p data/pdfs data/ocr_texts data/summaries data/vector_store

# 暴露端口
EXPOSE 5000

# 設定環境變數
ENV FLASK_APP=app/app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# 健康檢查
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:5000/ || exit 1

# 啟動應用程式
CMD ["python", "app/app.py"]
