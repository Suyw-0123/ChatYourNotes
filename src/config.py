import os
from dotenv import load_dotenv

# 載入環境變數
load_dotenv()

class Config:
    # LLM 設定（Gemini/OpenAI 二擇一）
    PROVIDER = os.getenv('LLM_PROVIDER', 'gemini')  # gemini 或 openai
    # Gemini 設定
    GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')
    GEMINI_MODEL = os.getenv('GEMINI_MODEL', 'models/gemini-1.5-flash-latest')
    # OpenAI 設定（保留向下相容）
    OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
    OPENAI_MODEL = os.getenv('OPENAI_MODEL', 'gpt-3.5-turbo')
    EMBEDDING_MODEL = os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002')

    # 檔案路徑設定
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_DIR = os.path.join(BASE_DIR, 'data')
    PDF_DIR = os.path.join(DATA_DIR, 'pdfs')
    OCR_DIR = os.path.join(DATA_DIR, 'ocr_texts')
    SUMMARY_DIR = os.path.join(DATA_DIR, 'summaries')
    VECTOR_STORE_DIR = os.path.join(DATA_DIR, 'vector_store')

    # 文本處理設定
    CHUNK_SIZE = int(os.getenv('CHUNK_SIZE', 1000))
    CHUNK_OVERLAP = int(os.getenv('CHUNK_OVERLAP', 200))

    # 檢索設定
    TOP_K = 5
    
    # 智能檢索設定
    ADAPTIVE_RETRIEVAL = True
    MIN_TOP_K = 3              # 最少檢索數量
    MAX_TOP_K = 20             # 最多檢索數量
    SIMILARITY_THRESHOLD = 0.7  # 相似度閾值
    CONTEXT_EXPANSION = True    # 啟用上下文擴展
    
    # Token 預算管理
    MAX_CONTEXT_TOKENS = 4000   # 給 LLM 的最大 context token
    QUESTION_COMPLEXITY_THRESHOLD = 50  # 問題複雜度判斷閾值（字符數）
    
    # 問題分析設定
    BROAD_QUESTION_KEYWORDS = [
        '整篇', '全部', '所有', '完整', '詳細解釋', '總結', '概述', 
        '整體', '全面', '綜合', 'overall', 'entire', 'complete', 'comprehensive'
    ]

    @classmethod
    def ensure_directories(cls):
        """確保所有必要的目錄都存在"""
        directories = [
            cls.DATA_DIR, cls.PDF_DIR, cls.OCR_DIR, 
            cls.SUMMARY_DIR, cls.VECTOR_STORE_DIR
        ]
        for directory in directories:
            os.makedirs(directory, exist_ok=True)