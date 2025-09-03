# 新用戶快速測試指南

這個文件幫助新用戶快速驗證安裝是否成功。

## 快速測試步驟

### 1. 環境測試

#### UV 環境測試
```bash
# 檢查 UV 是否安裝
uv --version

# 檢查 Python 環境
uv run python --version

# 測試關鍵套件導入
uv run python -c "import flask, chromadb, google.generativeai; print('✅ 所有關鍵套件正常')"
```

#### Docker 環境測試
```bash
# 檢查 Docker
docker --version
docker compose --version

# 檢查服務狀態
docker compose ps

# 測試 Web 應用回應
curl http://localhost:5000 -UseBasicParsing | Select-Object StatusCode
curl http://localhost:80 -UseBasicParsing | Select-Object StatusCode
```

### 2. 功能測試

#### 基本功能測試
1. 開啟瀏覽器訪問應用
2. 上傳一個簡單的 PDF 文件
3. 等待處理完成
4. 提問測試：「請總結這份文件的主要內容」
5. 檢查是否有合理的回應

#### API 測試
```python
# 創建測試腳本 test_api.py
from src.qa_service import QAService

try:
    qa_service = QAService()
    print("✅ QA 服務初始化成功")
    
    # 測試基本問答（需要先上傳文件）
    result = qa_service.answer_question("測試問題")
    print("✅ API 基本功能正常")
    
except Exception as e:
    print(f"❌ 測試失敗: {e}")
```

### 3. 常見測試問題

#### 問題：UV 命令不存在
**解決方案：**
```bash
# Windows PowerShell
powershell -c "irm https://astral.sh/uv/install.ps1 | iex"

# 重新啟動終端後測試
uv --version
```

#### 問題：Docker 服務啟動失敗
**解決方案：**
```bash
# 確保 Docker Desktop 正在運行
docker info

# 重新建構並啟動
docker compose down
docker compose up --build -d
```

#### 問題：API 金鑰錯誤
**解決方案：**
1. 檢查 `.env` 文件是否存在
2. 確認 API 金鑰格式正確
3. 測試 API 連接：
```bash
uv run python -c "
import os
from dotenv import load_dotenv
load_dotenv()
print('Gemini Key:', os.getenv('GEMINI_API_KEY')[:10] + '...' if os.getenv('GEMINI_API_KEY') else 'Not Found')
"
```

#### 問題：端口被佔用
**解決方案：**
```bash
# 檢查端口使用
netstat -an | findstr :5000    # Windows
lsof -i :5000                  # Linux/Mac

# 如果被佔用，修改 docker-compose.yml 中的端口
# 例如將 "5000:5000" 改為 "8080:5000"
```

### 4. 性能基準測試

#### 簡單性能測試
```python
import time
from src.qa_service import QAService

# 測試查詢回應時間
qa_service = QAService()
start_time = time.time()

# 執行查詢（需要先有文件）
result = qa_service.answer_question("簡單測試問題")

end_time = time.time()
response_time = end_time - start_time

print(f"查詢回應時間: {response_time:.2f} 秒")

if response_time < 10:
    print("✅ 性能正常")
else:
    print("⚠️ 回應時間較長，可能需要優化")
```

## 成功標準

如果以下檢查都通過，說明安裝成功：

- [ ] UV 或 Docker 環境正常啟動
- [ ] Web 介面可以正常訪問
- [ ] 可以成功上傳 PDF 文件
- [ ] OCR 處理正常完成
- [ ] 問答功能正常回應
- [ ] 查詢回應時間在合理範圍內（< 15秒）

## 需要幫助？

如果測試失敗，請：

1. 查看 README.md 中的故障排除部分
2. 檢查 `.env` 文件配置
3. 查看應用日誌尋找錯誤信息
4. 在 GitHub Issues 中尋找類似問題
5. 創建新的 Issue 並附上錯誤日誌

祝您使用愉快！🎉
