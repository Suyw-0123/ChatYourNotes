# ChatYourNotes 環境設置完成

## 🎉 恭喜！您的 ChatYourNotes 專案已成功設置 UV 環境和 Docker 運行環境

### 📁 專案結構
```
ChatYourNotes/
├── .venv/                 # UV 虛擬環境
├── app/                   # Flask 應用程序
├── src/                   # 核心程式碼
├── data/                  # 資料存儲目錄
├── .env                   # 環境配置文件
├── pyproject.toml         # UV 專案配置
├── requirements.txt       # Python 依賴
├── Dockerfile            # Docker 映像檔
├── docker-compose.yml    # Docker Compose 配置
└── 啟動腳本
```

### 🔧 環境配置

#### UV 環境
- **Python 版本**: 3.13.6
- **虛擬環境**: `.venv/`
- **套件管理**: UV (已安裝所有依賴)

#### Docker 環境
- **主應用服務**: 端口 5000
- **Nginx 反向代理**: 端口 80
- **Redis 快取**: 端口 6379

### 🚀 使用方法

#### 1. UV 環境本地運行
```powershell
# 使用 PowerShell 腳本
./start_uv.ps1

# 或手動運行
uv run python app/app.py
```

#### 2. Docker 環境運行
```powershell
# 啟動所有服務
docker compose up -d

# 檢查服務狀態
docker compose ps

# 檢查日誌
docker compose logs chatyournotes

# 停止服務
docker compose down
```

### 🌐 訪問應用程序

- **直接訪問**: http://localhost:5000
- **通過 Nginx**: http://localhost:80

### ⚙️ 環境變數配置

請編輯 `.env` 文件來配置您的 API 金鑰：

```env
# 選擇您的 LLM 提供者
LLM_PROVIDER=gemini  # 或 openai

# Gemini API 配置
GEMINI_API_KEY=your_gemini_api_key_here

# 或 OpenAI API 配置  
# OPENAI_API_KEY=your_openai_api_key_here
```

### 📋 已安裝的主要套件

- Flask (Web 框架)
- ChromaDB (向量資料庫)
- LangChain (LLM 框架)
- OpenAI / Google Generative AI (LLM APIs)
- PyTesseract (OCR)
- PDF2Image (PDF 處理)
- Sentence Transformers (嵌入模型)

### 🛠️ 開發工具

- **套件管理**: `uv sync` (同步依賴)
- **添加套件**: `uv add package_name`
- **運行腳本**: `uv run python script.py`

### 📝 注意事項

1. 確保在 `.env` 文件中設置正確的 API 金鑰
2. `data/` 目錄用於存儲上傳的文件和向量資料庫
3. Docker 容器會自動重啟（除非手動停止）
4. 使用 Nginx 可以提供更好的靜態文件服務和負載均衡

### 🔍 故障排除

如果遇到問題，請檢查：
- Docker 是否正在運行
- 端口 5000 和 80 是否被佔用
- .env 文件是否正確配置
- UV 環境是否正確安裝所有依賴

### 📞 支援

如需更多幫助，請檢查日誌：
```powershell
# UV 環境日誌直接在終端顯示
# Docker 日誌
docker compose logs chatyournotes
```

---
**✅ 設置完成！您的 ChatYourNotes 專案現在可以在 UV 環境和 Docker 中正常運行。**
