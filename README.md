# PDF 問答系統 (PDF QA System)

一個基於 RAG（Retrieval-Augmented Generation）架構的 PDF 文檔問答系統，支援中文 OCR 和智慧問答功能。(目前僅初步架構設計，仍需修正)

## 功能特色

- 📄 **PDF 上傳處理**：支援 PDF 檔案上傳和儲存
- 🔍 **智慧 OCR**：自動文字提取，支援中英文內容
- 📝 **AI 摘要**：使用 GPT 生成文檔摘要
- 🧠 **向量檢索**：基於語義相似度的文檔檢索
- 💬 **智慧問答**：結合檢索內容的 AI 問答
- 🌐 **Web 介面**：友善的網頁介面，支援拖放上傳
- 📊 **信心度評分**：問答結果包含信心度指標

## 系統架構

```
flowchart TD
    A[用戶上傳 PDF] --> B[File Handler]
    B --> C[儲存原檔案 data/pdfs]
    C --> D[OCR Reader - 轉文字]
    D --> E[儲存 OCR 結果 data/ocr_texts]
    E --> F[Summarizer - LLM 摘要]
    F --> G[儲存摘要 data/summaries]
    E --> H[Embedding + Chunking]
    H --> I[寫入向量資料庫 data/vector_store]
    
    J[用戶提問] --> K[QA Service]
    K --> L[檢索向量資料庫 - TopK]
    L --> M[將檢索內容 + 問題送給 LLM]
    M --> N[生成回答]
    N --> O[回傳給用戶]
```

## 環境需求

- Python 3.8+
- OpenAI API Key
- Tesseract OCR (用於圖像文字識別)

### 系統依賴 (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-chi-tra poppler-utils
```

### 系統依賴 (macOS)
```bash
brew install tesseract tesseract-lang poppler
```

### 系統依賴 (Windows)
1. 下載並安裝 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
2. 下載並安裝 [Poppler](https://poppler.freedesktop.org/)
3. 將安裝路徑添加到系統 PATH

## 安裝步驟

### 1. 克隆專案
```bash
git clone <repository-url>
cd pdf-qa-system
```

### 2. 創建虛擬環境
```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows
```

### 3. 安裝依賴
```bash
pip install -r requirements.txt
```

### 4. 環境設定
創建 `.env` 檔案：
```bash
cp .env.example .env
```

編輯 `.env` 檔案，填入你的 OpenAI API Key：
```env
OPENAI_API_KEY=your_openai_api_key_here
OPENAI_MODEL=gpt-3.5-turbo
EMBEDDING_MODEL=text-embedding-ada-002
CHUNK_SIZE=1000
CHUNK_OVERLAP=200
```

### 5. 初始化資料夾
```bash
python -c "from src.config import Config; Config.ensure_directories()"
```

## 使用方法

### 1. 啟動 Web 應用
```bash
cd app
python app.py
```

系統將在 http://localhost:5000 啟動

### 2. 使用流程
1. **上傳 PDF**：將 PDF 檔案拖放到上傳區域或點擊選擇
2. **等待處理**：系統會自動進行 OCR、摘要生成和向量化
3. **開始提問**：在右側對話框中輸入問題
4. **查看回答**：系統會提供答案、來源和信心度

### 3. API 使用
```python
from src.qa_service import QAService

qa_service = QAService()
result = qa_service.answer_question("什麼是機器學習？")
print(result['answer'])
```

## 專案結構

```
pdf-qa-system/
│
├── app/
│   ├── app.py              # Flask Web 應用
│   └── templates/
│       └── index.html      # 前端介面
│
├── src/
│   ├── config.py           # 設定檔
│   ├── file_handler.py     # 檔案處理
│   ├── ocr_reader.py       # OCR 文字提取
│   ├── summarizer.py       # AI 摘要生成
│   ├── vector_store.py     # 向量資料庫
│   └── qa_service.py       # 問答服務
│
├── data/
│   ├── pdfs/              # 原始 PDF 檔案
│   ├── ocr_texts/         # OCR 提取的文字
│   ├── summaries/         # 生成的摘要
│   └── vector_store/      # ChromaDB 向量資料庫
│
├── notebook/
│   └── playground.ipynb   # 開發測試筆記本
│
├── requirements.txt       # Python 依賴
├── .env                  # 環境變數 (需自行創建)
└── README.md
```

## 核心組件說明

### 1. OCR Reader (ocr_reader.py)
- 支援直接文字提取和 OCR 影像識別
- 自動選擇最佳提取方法
- 支援中英文內容

### 2. Summarizer (summarizer.py)
- 使用 OpenAI GPT 生成摘要
- 支援長文檔分段摘要
- 結構化摘要輸出

### 3. Vector Store (vector_store.py)
- 基於 ChromaDB 的向量資料庫
- 使用 Sentence Transformers 進行文檔嵌入
- 支援語義相似度搜索

### 4. QA Service (qa_service.py)
- 整合檢索和生成的問答服務
- 提供信心度評分
- 支援多文檔檢索

## 設定說明

### 環境變數
- `OPENAI_API_KEY`: OpenAI API 金鑰
- `OPENAI_MODEL`: GPT 模型名稱 (預設: gpt-3.5-turbo)
- `CHUNK_SIZE`: 文檔分塊大小 (預設: 1000)
- `CHUNK_OVERLAP`: 分塊重疊長度 (預設: 200)

### 檔案路徑
所有資料檔案都儲存在 `data/` 目錄下：
- `data/pdfs/`: 原始 PDF 檔案
- `data/ocr_texts/`: OCR 提取的純文字
- `data/summaries/`: AI 生成的摘要
- `data/vector_store/`: ChromaDB 資料庫檔案

## 開發和測試

### 使用 Jupyter Notebook
```bash
cd notebook
jupyter notebook playground.ipynb
```

筆記本包含：
- 各組件單元測試
- 完整流程測試
- 效能基準測試

### 測試 API
```python
# 測試問答功能
from src.qa_service import QAService

qa = QAService()
result = qa.answer_question("請問這份文件的主要內容是什麼？")
print(f"答案: {result['answer']}")
print(f"信心度: {result['confidence']}")
```

## 常見問題

### 1. OCR 無法正常工作
確認 Tesseract 已正確安裝：
```bash
tesseract --version
```

### 2. 中文字識別效果不佳
確認已安裝中文語言包：
```bash
# Ubuntu/Debian
sudo apt install tesseract-ocr-chi-tra tesseract-ocr-chi-sim

# macOS
brew install tesseract-lang
```

### 3. OpenAI API 錯誤
檢查 API Key 是否正確設定：
```python
import openai
print(openai.api_key)  # 確認 key 已載入
```

### 4. 向量資料庫錯誤
刪除並重新建立向量資料庫：
```bash
rm -rf data/vector_store/*
```

## 進階設定

### 自訂嵌入模型
修改 `src/vector_store.py` 中的模型：
```python
self.embedding_model = SentenceTransformer('your-model-name')
```

### 調整檢索參數
修改 `src/config.py` 中的設定：
```python
TOP_K = 10  # 增加檢索文檔數量
CHUNK_SIZE = 1500  # 增加文檔塊大小
```

## 效能優化

### 1. 硬體需求
- **RAM**: 建議 8GB+ (向量計算需要較多記憶體)
- **儲存**: SSD 硬碟 (提升資料庫讀寫速度)
- **CPU**: 多核心處理器 (OCR 處理)

### 2. 軟體優化
- 使用 GPU 加速的嵌入模型
- 快取常用查詢結果
- 分批處理大型文檔

## 部署建議

### 1. 本機開發
```bash
python app/app.py
```

### 2. 生產環境
使用 Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

### 3. Docker 部署
```dockerfile
FROM python:3.8-slim

# 安裝系統依賴
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-chi-tra \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app/app.py"]
```

## 貢獻指南

1. Fork 專案
2. 創建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交變更 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 開啟 Pull Request

## 授權條款

此專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 聯絡資訊

如有問題或建議，請開啟 GitHub Issue 或聯絡專案維護者。

---

**注意**: 使用此系統前請確保已正確設定 OpenAI API Key，並遵守相關使用條款。