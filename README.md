# PDF 問答系統 (PDF QA System) 

一個基於 RAG（Retrieval-Augmented Generation）架構的 PDF 文檔問答系統，支援中文 OCR 和 Gemini 智慧問答功能，具備智能檢索和上下文擴展策略。

## 🚀 快速開始

### 方式一：UV 環境（推薦新用戶）

UV 是現代 Python 套件管理器，提供最快速的安裝體驗：

```bash
# 1. 克隆專案
git clone https://github.com/Suyw-0123/ChatYourNotes.git
cd ChatYourNotes

# 2. 設置 UV 環境（自動安裝 Python 3.13.6）
uv venv
# Windows
.venv\Scripts\activate
# Linux/Mac  
source .venv/bin/activate

# 3. 安裝依賴
uv sync

# 4. 配置環境變數
cp .env.example .env
# 編輯 .env 文件，填入您的 API Key

# 5. 啟動應用
uv run python app/app.py
# 或使用提供的啟動腳本
./start_uv.ps1  # Windows PowerShell
./start_uv.bat  # Windows 批次檔
```

### 方式二：Docker 容器化部署（推薦生產環境）

```bash
# 1. 克隆專案
git clone https://github.com/Suyw-0123/ChatYourNotes.git
cd ChatYourNotes

# 2. 配置環境變數
cp .env.example .env
# 編輯 .env 文件，填入您的 API Key

# 3. 啟動完整服務（包含 Nginx + Redis）
docker compose up -d

# 4. 檢查服務狀態
docker compose ps
```

應用程式將在以下地址運行：
- **UV 環境**: http://localhost:5000
- **Docker**: http://localhost:80（Nginx 反向代理）

## 📋 環境配置

### 1. 必需的 API 金鑰

創建 `.env` 文件並配置：

```env
# 選擇您的 LLM 提供者
LLM_PROVIDER=gemini  # 或 openai

# Gemini API 配置（推薦）
GEMINI_API_KEY=your_gemini_api_key_here
GEMINI_MODEL=models/gemini-1.5-flash-latest

# 或 OpenAI API 配置
# OPENAI_API_KEY=your_openai_api_key_here
# OPENAI_MODEL=gpt-3.5-turbo

# Flask 配置
FLASK_ENV=development
FLASK_DEBUG=True
```

### 2. 如何獲取 API 金鑰

#### Gemini API（推薦）
1. 訪問 [Google AI Studio](https://aistudio.google.com/)
2. 點擊「Get API Key」
3. 創建新項目或選擇現有項目
4. 複製 API 金鑰到 `.env` 文件

#### OpenAI API
1. 訪問 [OpenAI Platform](https://platform.openai.com/)
2. 註冊並登入帳戶
3. 進入 API Keys 頁面
4. 創建新的 API 金鑰
5. 複製到 `.env` 文件

## 🛠️ 安裝方式詳解

### UV 環境安裝（推薦開發）

#### 優勢
- ✅ **超快速**：比 pip 快 10-100 倍
- ✅ **自動化**：自動管理 Python 版本
- ✅ **隔離性**：完全獨立的環境
- ✅ **跨平台**：Windows、Mac、Linux 一致體驗

#### 安裝 UV（如果尚未安裝）

**Windows (PowerShell):**
```powershell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
```

**Linux/Mac:**
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

#### 使用 UV 啟動專案

```bash
# 一鍵啟動（Windows PowerShell）
./start_uv.ps1

# 一鍵啟動（Windows 批次檔）
./start_uv.bat

# 手動啟動
uv run python app/app.py
```

## 功能特色

- 📄 **PDF 上傳處理**：支援 PDF 檔案上傳和儲存
- 🔍 **智慧 OCR**：自動文字提取，支援中英文內容
- 📝 **AI 摘要**：使用 Gemini 生成文檔摘要
- 🧠 **智能向量檢索**：基於語義相似度的文檔檢索，支援自適應檢索策略
- � **上下文擴展**：自動擴展相關文檔片段，提供更完整的上下文
- 🎯 **問題分析**：自動分析問題複雜度並調整檢索策略
- 📊 **問題分解**：將廣泛性問題分解為子問題，提供更全面的回答
- �💬 **智慧問答**：結合檢索內容的 AI 問答，支援 Markdown 格式回答
- 🌐 **Web 介面**：友善的網頁介面，支援拖放上傳
- � **信心度評分**：問答結果包含詳細的信心度指標和來源分析
- ⚙️ **Token 預算管理**：智能管理上下文長度，避免超出模型限制

## 智能檢索功能

### 1. Context 擴展策略
- **多階檢索**：先取 Top-K 高相似度片段，再檢查相鄰文檔片段
- **問題分解**：自動識別廣泛性問題（如「解釋整篇筆記」），分解為多個子問題
- **上下文擴展**：基於文檔片段的連續性和相關性，自動擴展檢索範圍

### 2. 資訊量自適應
- **複雜度檢測**：根據問題長度、關鍵詞分析問題複雜度
- **動態檢索**：
  - 簡單問題：減少檢索數量，提高相似度閾值
  - 複雜問題：增加檢索數量，放寬相似度限制
  - 廣泛問題：使用問題分解策略
- **Token 預算管理**：自動控制上下文長度，確保不超過模型限制

### 3. 檢索品質提升
- **相似度評分**：提供詳細的文檔片段相似度資訊
- **來源標記**：標示檢索結果的relevance level（high/medium/low）
- **信心度計算**：基於檢索結果品質和覆蓋範圍計算綜合信心度

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

### Docker 容器化部署

#### 優勢

- ✅ **零環境配置**：無需安裝 Python、Tesseract 等依賴
- ✅ **一致性**：開發、測試、生產環境完全一致
- ✅ **快速部署**：一鍵啟動整個應用堆疊
- ✅ **易於擴展**：可輕鬆添加負載均衡、快取等服務
- ✅ **資料持久化**：透過 Volume 掛載確保資料不丟失

#### 使用 Docker Compose（推薦）

```bash
# 1. 克隆專案
git clone https://github.com/Suyw-0123/ChatYourNotes.git
cd ChatYourNotes

# 2. 配置環境變數
cp .env.example .env
# 編輯 .env 文件，填入您的 API Key

# 3. 啟動完整服務堆疊
docker compose up -d

# 4. 檢查服務狀態
docker compose ps

# 5. 查看日誌（如需要）
docker compose logs chatyournotes

# 6. 停止服務
docker compose down
```

**服務包含：**
- **主應用**: ChatYourNotes (端口 5000)
- **Nginx**: 反向代理 (端口 80)
- **Redis**: 快取服務 (端口 6379)

#### 僅使用 Docker

```bash
# 建構映像
docker build -t chatyournotes .

# 運行容器
docker run -d \
  --name chatyournotes \
  -p 5000:5000 \
  -v $(pwd)/data:/app/data \
  --env-file .env \
  chatyournotes
```

#### 生產環境部署

```bash
# 使用生產配置
docker compose -f docker-compose.prod.yml up -d
```

### 傳統 Python 環境安裝

#### 系統依賴安裝

**Ubuntu/Debian:**
```bash
sudo apt update
sudo apt install tesseract-ocr tesseract-ocr-chi-tra poppler-utils
```

**macOS:**
```bash
brew install tesseract tesseract-lang poppler
```

**Windows:**
1. 下載並安裝 [Tesseract OCR](https://github.com/UB-Mannheim/tesseract/wiki)
2. 下載並安裝 [Poppler](https://poppler.freedesktop.org/)
3. 將安裝路徑添加到系統 PATH

#### Python 環境設置

```bash
# 1. 克隆專案
git clone https://github.com/Suyw-0123/ChatYourNotes.git
cd ChatYourNotes

# 2. 創建虛擬環境
python -m venv venv
source venv/bin/activate  # Linux/Mac
# 或
venv\Scripts\activate     # Windows

# 3. 安裝依賴
pip install -r requirements.txt

# 4. 配置環境變數
cp .env.example .env
# 編輯 .env 文件

# 5. 初始化資料夾
python -c "from src.config import Config; Config.ensure_directories()"

# 6. 啟動應用
python app/app.py
```

## 📖 使用方法

### 1. 啟動應用

**UV 環境:**
```bash
uv run python app/app.py
# 或使用啟動腳本
./start_uv.ps1  # PowerShell
./start_uv.bat  # 批次檔
```

**Docker:**
```bash
docker compose up -d
```

### 2. 訪問應用

- **UV 環境**: <http://localhost:5000>
- **Docker**: <http://localhost:80>（通過 Nginx）

### 3. 操作流程

1. **上傳 PDF**：將 PDF 檔案拖放到上傳區域或點擊選擇
2. **等待處理**：系統會自動進行 OCR、摘要生成和向量化
3. **開始提問**：在右側對話框中輸入問題
   
   ⚠️ **重要提醒**：如果您上傳的是英文內容的文件，請使用英文提問
4. **查看回答**：系統會提供答案、來源和信心度

### 4. API 使用範例

```python
from src.qa_service import QAService

qa_service = QAService()
result = qa_service.answer_question("什麼是機器學習？")
print(result['answer'])
```

## 🛠️ 故障排除

### 常見問題解決

#### 1. UV 環境問題

**問題：uv 命令未找到**
```bash
# 重新安裝 UV
# Windows
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"
# Linux/Mac
curl -LsSf https://astral.sh/uv/install.sh | sh
```

**問題：套件安裝失敗**
```bash
# 清除快取重新安裝
uv cache clean
uv sync --reinstall
```

#### 2. Docker 問題

**問題：Docker 服務無法啟動**
```bash
# 檢查 Docker 是否運行
docker --version
docker compose --version

# 重新建構映像
docker compose down
docker compose build --no-cache
docker compose up -d
```

**問題：端口被佔用**
```bash
# 檢查端口使用情況
netstat -an | find "5000"  # Windows
lsof -i :5000              # Linux/Mac

# 修改端口（編輯 docker-compose.yml）
ports:
  - "8080:5000"  # 使用 8080 替代 5000
```

#### 3. API 金鑰問題

**問題：Gemini API 錯誤**
```bash
# 檢查 API 金鑰是否正確設置
cat .env | grep GEMINI_API_KEY

# 測試 API 連接
uv run python -c "import google.generativeai as genai; genai.configure(api_key='your_key'); print('API 連接正常')"
```

**問題：配額超限**
- 檢查 [Google AI Studio](https://aistudio.google.com/) 的使用限制
- 考慮升級到付費方案或使用 OpenAI API

#### 4. OCR 問題

**問題：OCR 無法正常工作**
```bash
# 檢查 Tesseract 安裝
tesseract --version

# 重新安裝（Ubuntu/Debian）
sudo apt-get remove tesseract-ocr
sudo apt-get install tesseract-ocr tesseract-ocr-chi-tra

# Docker 環境下無需額外配置
```

**問題：中文識別效果不佳**
- 確保 PDF 圖像清晰度足夠
- 嘗試調整 OCR 參數（在 `src/ocr_reader.py` 中）
- 使用更高解析度的 PDF

#### 5. 向量資料庫問題

**問題：向量資料庫錯誤**
```bash
# 刪除並重新建立向量資料庫
rm -rf data/vector_store/*
# 重新上傳 PDF 進行處理
```

**問題：檢索結果不準確**
- 調整 `CHUNK_SIZE` 和 `CHUNK_OVERLAP` 參數
- 檢查文檔內容是否適合分塊
- 考慮使用不同的嵌入模型

#### 6. 記憶體問題

**問題：系統記憶體不足**
```bash
# 調整 Docker 記憶體限制
# 在 docker-compose.yml 中添加：
services:
  chatyournotes:
    mem_limit: 2g
    memswap_limit: 2g
```

**問題：UV 環境記憶體不足**
- 關閉其他應用程序
- 減少 `CHUNK_SIZE` 參數
- 分批處理大型文檔

### 效能優化建議

#### 硬體建議
- **RAM**: 8GB+ （推薦 16GB）
- **儲存**: SSD 硬碟
- **CPU**: 4核心以上

#### 軟體優化
```python
# 調整配置參數（src/config.py）
CHUNK_SIZE = 800        # 減少記憶體使用
TOP_K = 5              # 減少檢索數量
MAX_TOKENS = 2000      # 限制回應長度
```

### 日誌查看

**UV 環境:**
- 日誌直接顯示在終端

**Docker 環境:**
```bash
# 查看應用日誌
docker compose logs chatyournotes

# 即時查看日誌
docker compose logs -f chatyournotes

# 查看所有服務日誌
docker compose logs
```

### 資料備份

```bash
# 備份重要資料
tar -czf chatyournotes_backup.tar.gz data/

# 恢復資料
tar -xzf chatyournotes_backup.tar.gz
```

## 📁 專案結構

```
ChatYourNotes/
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
│   ├── qa_service.py       # 問答服務
│   ├── smart_retrieval.py  # 智能檢索策略
│   └── language_service.py # 語言檢測服務
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
├── .venv/                 # UV 虛擬環境
├── .env.example           # 環境變數模板
├── .env                   # 環境變數（需自行創建）
├── pyproject.toml         # UV 專案配置
├── requirements.txt       # Python 依賴
├── uv.lock               # UV 依賴鎖定檔
├── Dockerfile            # Docker 映像配置
├── docker-compose.yml    # Docker Compose 配置
├── docker-compose.prod.yml # 生產環境 Docker 配置
├── nginx.conf            # Nginx 配置
├── start_uv.ps1          # PowerShell 啟動腳本
├── start_uv.bat          # Windows 批次啟動腳本
└── README.md             # 專案說明文件
```

## ⚙️ 配置說明

### 環境變數

| 變數名 | 說明 | 預設值 | 必需 |
|--------|------|--------|------|
| `LLM_PROVIDER` | LLM 提供者 | `gemini` | ✅ |
| `GEMINI_API_KEY` | Gemini API 金鑰 | - | ✅ |
| `GEMINI_MODEL` | Gemini 模型 | `models/gemini-1.5-flash-latest` | ❌ |
| `OPENAI_API_KEY` | OpenAI API 金鑰 | - | ❌ |
| `OPENAI_MODEL` | OpenAI 模型 | `gpt-3.5-turbo` | ❌ |
| `CHUNK_SIZE` | 文檔分塊大小 | `1000` | ❌ |
| `CHUNK_OVERLAP` | 分塊重疊長度 | `200` | ❌ |
| `TOP_K` | 檢索文檔數量 | `10` | ❌ |
| `FLASK_ENV` | Flask 環境 | `development` | ❌ |

### 檔案路徑

所有資料檔案都儲存在 `data/` 目錄下，支援自動創建：

- `data/pdfs/`: 原始 PDF 檔案
- `data/ocr_texts/`: OCR 提取的純文字
- `data/summaries/`: AI 生成的摘要
- `data/vector_store/`: ChromaDB 資料庫檔案

## 🔧 核心組件

### 1. OCR Reader (`ocr_reader.py`)

- 支援直接文字提取和 OCR 影像識別
- 自動選擇最佳提取方法
- 支援中英文內容
- 使用 Tesseract OCR 引擎

### 2. Summarizer (`summarizer.py`)

- 使用 Gemini 生成摘要
- 支援長文檔分段摘要
- 結構化摘要輸出
- 自動語言檢測

### 3. Vector Store (`vector_store.py`)

- 基於 ChromaDB 的向量資料庫
- 使用 Sentence Transformers 進行文檔嵌入
- 支援語義相似度搜索
- 自動文檔分塊和索引

### 4. QA Service (`qa_service.py`)

- 整合檢索和生成的問答服務
- 提供信心度評分
- 支援多文檔檢索
- Markdown 格式回應

### 5. Smart Retrieval (`smart_retrieval.py`)

- 智能檢索策略
- 問題複雜度分析
- 上下文擴展
- 動態檢索調整

## 📊 效能指標

### 推薦硬體配置

| 組件 | 最低需求 | 推薦配置 | 說明 |
|------|----------|----------|------|
| RAM | 4GB | 8GB+ | 向量計算需要較多記憶體 |
| 儲存 | 10GB | SSD 50GB+ | 提升資料庫讀寫速度 |
| CPU | 雙核 | 四核+ | OCR 處理和並行處理 |
| 網路 | - | 穩定連線 | API 呼叫需求 |

### 處理速度參考

| 文檔大小 | OCR 時間 | 向量化時間 | 查詢回應時間 |
|----------|----------|------------|--------------|
| 1-5頁 | 10-30秒 | 5-15秒 | 2-5秒 |
| 6-20頁 | 30-90秒 | 15-45秒 | 3-8秒 |
| 21-50頁 | 90-180秒 | 45-120秒 | 5-15秒 |

*時間因硬體配置和文檔複雜度而異

## 🤝 貢獻指南

我們歡迎社群貢獻！請遵循以下流程：

### 1. 準備開發環境

```bash
# Fork 並克隆專案
git clone https://github.com/YOUR_USERNAME/ChatYourNotes.git
cd ChatYourNotes

# 設置 UV 開發環境
uv venv
uv sync

# 創建功能分支
git checkout -b feature/amazing-feature
```

### 2. 開發規範

- 遵循 PEP 8 編碼規範
- 添加適當的註解和文檔字串
- 編寫單元測試
- 更新相關文檔

### 3. 測試

```bash
# 運行測試
uv run python -m pytest

# 檢查程式碼風格
uv run python -m flake8 src/

# 類型檢查
uv run python -m mypy src/
```

### 4. 提交流程

```bash
# 提交變更
git add .
git commit -m "feat: 添加令人驚豔的新功能"

# 推送到您的 Fork
git push origin feature/amazing-feature

# 在 GitHub 上創建 Pull Request
```

### 5. Pull Request 指南

- 清楚描述變更內容和動機
- 附上相關的 Issue 編號
- 確保所有測試通過
- 更新相關文檔

## 📄 授權條款

此專案採用 MIT 授權條款 - 詳見 [LICENSE](LICENSE) 檔案

## 📞 支援與聯絡

### 獲取幫助

- 📖 **文檔**: 查看本 README 和程式碼註解
- 🐛 **Bug 回報**: [GitHub Issues](https://github.com/Suyw-0123/ChatYourNotes/issues)
- 💡 **功能建議**: [GitHub Discussions](https://github.com/Suyw-0123/ChatYourNotes/discussions)
- ❓ **使用問題**: [GitHub Issues](https://github.com/Suyw-0123/ChatYourNotes/issues) 標記為 `question`

### 專案資訊

- **維護者**: Suyw-0123
- **專案狀態**: 積極開發中
- **版本**: 查看 [Releases](https://github.com/Suyw-0123/ChatYourNotes/releases)
- **更新日誌**: [CHANGELOG.md](CHANGELOG.md)

### 社群

- 🌟 **給個星星**: 如果這個專案對您有幫助，請給個 ⭐
- 🔄 **分享**: 歡迎分享給需要的朋友
- 📢 **關注**: Watch 此專案獲取最新更新

---

## ⚠️ 重要提醒

1. **API 金鑰安全**: 請勿將 API 金鑰提交到版本控制系統
2. **使用條款**: 請遵守 Gemini/OpenAI 的使用條款和政策
3. **資料隱私**: 上傳的文檔會在本地處理，請注意敏感資料保護
4. **網路需求**: 需要穩定的網路連線以使用 AI 服務
5. **成本注意**: 使用 API 可能產生費用，請留意使用量

**感謝使用 ChatYourNotes！** 🎉

如有任何問題或建議，歡迎隨時聯絡我們。
