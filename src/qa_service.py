
from typing import List, Dict
from src.config import Config
from src.vector_store import VectorStore

# Gemini
import google.generativeai as genai

# OpenAI（保留向下相容）
try:
    import openai
except ImportError:
    openai = None

class QAService:
    def __init__(self):
        self.vector_store = VectorStore()
        # Gemini 設定
        if Config.PROVIDER == 'gemini':
            genai.configure(api_key=Config.GEMINI_API_KEY)
        # OpenAI 設定
        if openai and Config.PROVIDER == 'openai':
            openai.api_key = Config.OPENAI_API_KEY

    def answer_question(self, question: str) -> Dict:
        """回答使用者問題（Gemini 或 OpenAI）"""
        try:
            print(f"Processing question: {question}")
            # 1. 從向量資料庫檢索相關內容
            relevant_docs = self.vector_store.search(question, Config.TOP_K)
            if not relevant_docs:
                return {
                    'answer': '抱歉，我找不到相關的資訊來回答您的問題。請確認您已上傳相關的 PDF 文件。',
                    'sources': [],
                    'confidence': 0.0
                }
            # 2. 準備上下文
            context = self._prepare_context(relevant_docs)
            # 3. 生成回答
            if Config.PROVIDER == 'gemini':
                answer = self._generate_answer_gemini(question, context)
            else:
                answer = self._generate_answer_openai(question, context)
            # 4. 準備來源資訊
            sources = self._prepare_sources(relevant_docs)
            # 5. 計算信心分數（基於檢索結果的距離）
            confidence = self._calculate_confidence(relevant_docs)
            return {
                'answer': answer,
                'sources': sources,
                'confidence': confidence,
                'retrieved_docs': len(relevant_docs)
            }
        except Exception as e:
            print(f"Error in QA service: {str(e)}")
            return {
                'answer': f'處理問題時發生錯誤：{str(e)}',
                'sources': [],
                'confidence': 0.0
            }
    
    def _prepare_context(self, relevant_docs: List[Dict]) -> str:
        """準備上下文資料"""
        context_parts = []
        
        for i, doc in enumerate(relevant_docs):
            source_info = f"來源：{doc['metadata'].get('filename', '未知檔案')}"
            content = doc['content']
            context_parts.append(f"[片段 {i+1}] {source_info}\n{content}")
        
        return "\n\n".join(context_parts)
    
    def _generate_answer_gemini(self, question: str, context: str) -> str:
        """使用 Gemini 生成回答"""
        prompt = f"""
你是一個專業的文檔問答助手。請根據提供的上下文資訊來回答使用者的問題。

重要指示：
1. 只根據提供的上下文來回答問題
2. 如果上下文中沒有相關資訊，請明確說明
3. 回答要準確、簡潔且有幫助
4. 如果可能，請引用具體的來源
5. 使用繁體中文回答

上下文資訊：
{context}

使用者問題：{question}

請提供詳細且準確的回答：
"""
        try:
            model = genai.GenerativeModel(Config.GEMINI_MODEL)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating answer (Gemini): {str(e)}")
            return "抱歉，生成回答時發生錯誤（Gemini）。請稍後再試。"

    def _generate_answer_openai(self, question: str, context: str) -> str:
        """使用 OpenAI 生成回答（保留相容）"""
        if not openai:
            return "本系統未安裝 openai 套件，請改用 Gemini 或安裝 openai。"
        prompt = f"""
你是一個專業的文檔問答助手。請根據提供的上下文資訊來回答使用者的問題。

重要指示：
1. 只根據提供的上下文來回答問題
2. 如果上下文中沒有相關資訊，請明確說明
3. 回答要準確、簡潔且有幫助
4. 如果可能，請引用具體的來源
5. 使用繁體中文回答

上下文資訊：
{context}

使用者問題：{question}

請提供詳細且準確的回答：
"""
        try:
            response = openai.ChatCompletion.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一個專業的文檔問答助手，擅長根據提供的文檔內容回答問題。你會提供準確、有幫助的回答，並在必要時說明資訊的來源。"
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating answer (OpenAI): {str(e)}")
            return "抱歉，生成回答時發生錯誤（OpenAI）。請稍後再試。"
    
    def _prepare_sources(self, relevant_docs: List[Dict]) -> List[Dict]:
        """準備來源資訊"""
        sources = []
        seen_files = set()
        
        for doc in relevant_docs:
            filename = doc['metadata'].get('filename', '未知檔案')
            if filename not in seen_files:
                sources.append({
                    'filename': filename,
                    'chunk_info': f"片段 {doc['metadata'].get('chunk_index', 0) + 1}/{doc['metadata'].get('total_chunks', 1)}"
                })
                seen_files.add(filename)
        
        return sources
    
    def _calculate_confidence(self, relevant_docs: List[Dict]) -> float:
        """計算信心分數"""
        if not relevant_docs:
            return 0.0
        
        # 基於最佳匹配的距離計算信心分數
        best_distance = relevant_docs[0].get('distance', 1.0)
        
        # 距離越小，信心越高（距離範圍通常是 0-2）
        confidence = max(0.0, min(1.0, 1.0 - (best_distance / 2.0)))
        
        return round(confidence, 2)
    
    def get_available_documents(self) -> List[str]:
        """取得可用的文檔清單"""
        return self.vector_store.get_document_list()