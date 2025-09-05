
from typing import List, Dict
from src.config import Config
from src.vector_store import VectorStore
from src.smart_retrieval import SmartRetrievalService

# Gemini
import google.generativeai as genai

# OpenAI（保留向下相容）
try:
    import openai
except ImportError:
    openai = None

 

    def answer_question(self, question: str) -> Dict:
        """回答使用者問題（使用智能檢索策略）"""
        try:
            print(f"Processing question: {question}")
            
            # 1. 分析問題複雜度
            question_analysis = self.smart_retrieval.analyze_question_complexity(question)
            print(f"Question analysis: {question_analysis}")
            
            # 2. 處理廣泛性問題
            if question_analysis['is_broad']:
                return self._handle_broad_question(question)
            
            # 3. 使用自適應檢索
            relevant_docs = self.smart_retrieval.adaptive_retrieval(question)
            
            if not relevant_docs:
                return {
                    'answer': '抱歉，我找不到相關的資訊來回答您的問題。請確認您已上傳相關的 PDF 文件，或嘗試重新表述您的問題。',
                    'sources': [],
                    'confidence': 0.0
                }
            
            # 4. 準備智能上下文
            context = self._prepare_smart_context(relevant_docs, question)
            
            # 5. 生成回答
            if Config.PROVIDER == 'gemini':
                answer = self._generate_answer_gemini(question, context, question_analysis)
            else:
                answer = self._generate_answer_openai(question, context, question_analysis)
            
            # 6. 準備來源資訊
            sources = self._prepare_sources(relevant_docs)
            
            # 7. 計算信心分數
            confidence = self._calculate_enhanced_confidence(relevant_docs, question_analysis)
            
            return {
                'answer': answer,
                'sources': sources,
                'confidence': confidence,
                'retrieved_docs': len(relevant_docs),
                'question_analysis': question_analysis
            }
            
        except Exception as e:
            print(f"Error in QA service: {str(e)}")
            return {
                'answer': f'處理問題時發生錯誤：{str(e)}',
                'sources': [],
                'confidence': 0.0
            }
    
    def _handle_broad_question(self, question: str) -> Dict:
        """處理廣泛性問題"""
        print("Handling broad question with decomposition strategy...")
        
        # 分解問題
        sub_questions = self.smart_retrieval.decompose_broad_question(question)
        print(f"Decomposed into {len(sub_questions)} sub-questions")
        
        # 收集所有相關文檔
        all_relevant_docs = []
        for sub_q in sub_questions:
            docs = self.smart_retrieval.adaptive_retrieval(sub_q)
            all_relevant_docs.extend(docs)
        
        # 去重但保留順序
        seen_ids = set()
        unique_docs = []
        for doc in all_relevant_docs:
            doc_id = f"{doc['metadata'].get('filename', '')}_chunk_{doc['metadata'].get('chunk_index', 0)}"
            if doc_id not in seen_ids:
                seen_ids.add(doc_id)
                unique_docs.append(doc)
        
        # 限制文檔數量避免過載
        if len(unique_docs) > Config.MAX_TOP_K:
            unique_docs = unique_docs[:Config.MAX_TOP_K]
        
        # 準備綜合上下文
        context = self._prepare_comprehensive_context(unique_docs, question)
        
        # 生成綜合回答
        question_analysis = {'is_broad': True, 'complexity_score': 10}
        if Config.PROVIDER == 'gemini':
            answer = self._generate_comprehensive_answer_gemini(question, context, sub_questions)
        else:
            answer = self._generate_comprehensive_answer_openai(question, context, sub_questions)
        
        return {
            'answer': answer,
            'sources': self._prepare_sources(unique_docs),
            'confidence': self._calculate_enhanced_confidence(unique_docs, question_analysis),
            'retrieved_docs': len(unique_docs),
            'sub_questions': sub_questions
        }
    
    def _prepare_smart_context(self, relevant_docs: List[Dict], question: str) -> str:
        """準備智能上下文（含Token預算管理）"""
        context_parts = []
        
        for i, doc in enumerate(relevant_docs):
            source_info = f"來源：{doc['metadata'].get('filename', '未知檔案')}"
            chunk_info = f"片段 {doc['metadata'].get('chunk_index', 0) + 1}"
            confidence_info = f"相似度：{1 - doc.get('distance', 1):.2f}"
            
            content = doc['content']
            context_parts.append(f"[{chunk_info}] {source_info} ({confidence_info})\n{content}")
        
        # 使用Token預算管理
        managed_context = self.smart_retrieval.manage_token_budget(context_parts, question)
        return managed_context
    
    def _prepare_comprehensive_context(self, docs: List[Dict], question: str) -> str:
        """為廣泛問題準備綜合上下文"""
        # 按檔案名分組
        docs_by_file = {}
        for doc in docs:
            filename = doc['metadata'].get('filename', '未知檔案')
            if filename not in docs_by_file:
                docs_by_file[filename] = []
            docs_by_file[filename].append(doc)
        
        context_parts = []
        for filename, file_docs in docs_by_file.items():
            # 每個檔案的內容
            file_content = []
            for doc in sorted(file_docs, key=lambda x: x['metadata'].get('chunk_index', 0)):
                file_content.append(doc['content'])
            
            combined_content = "\n".join(file_content)
            context_parts.append(f"=== 檔案：{filename} ===\n{combined_content}")
        
        # Token預算管理
        return self.smart_retrieval.manage_token_budget(context_parts, question)
    
    def _generate_answer_gemini(self, question: str, context: str, question_analysis: Dict = None) -> str:
        """使用 Gemini 生成回答（增強版）"""
        # 根據問題複雜度調整 prompt
        if question_analysis and question_analysis.get('is_broad'):
            prompt = f"""
你是一個專業的文檔問答助手。用戶提出了一個廣泛性問題，需要綜合多個來源的資訊來回答。

重要指示：
1. 這是一個廣泛性問題，需要全面性的回答
2. 請根據提供的上下文資訊進行綜合分析
3. 組織答案結構：先概述，再詳細說明，最後總結
4. 如果資訊不足，請明確指出需要更多資訊的部分
5. 使用 Markdown 格式美化回答（標題、列表、粗體等）
6. 使用繁體中文回答

上下文資訊：
{context}

用戶問題：{question}

請提供全面且結構化的回答：
"""
        else:
            prompt = f"""
你是一個專業的文檔問答助手。請根據提供的上下文資訊來回答使用者的問題。

重要指示：
1. 只根據提供的上下文來回答問題
2. 如果上下文中沒有相關資訊，請明確說明
3. 回答要準確、簡潔且有幫助
4. 如果可能，請引用具體的來源
5. 使用 Markdown 格式美化回答（如需要）
6. 使用繁體中文回答

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
    
    def _generate_comprehensive_answer_gemini(self, question: str, context: str, sub_questions: List[str]) -> str:
        """為廣泛問題生成綜合回答（Gemini）"""
        prompt = f"""
你是一個專業的文檔問答助手。用戶提出了一個廣泛性問題，我已經將其分解為多個子問題並收集了相關資訊。

原始問題：{question}

分解的子問題：
{chr(10).join([f"- {sq}" for sq in sub_questions])}

綜合上下文資訊：
{context}

請根據上述資訊提供一個全面且結構化的回答：
1. 首先提供問題的總體概述
2. 然後按主題分別詳細說明
3. 最後進行總結
4. 使用 Markdown 格式美化回答
5. 如果某些方面資訊不足，請明確指出
6. 使用繁體中文回答

請提供詳細的綜合回答：
"""
        
        try:
            model = genai.GenerativeModel(Config.GEMINI_MODEL)
            response = model.generate_content(prompt)
            return response.text.strip()
        except Exception as e:
            print(f"Error generating comprehensive answer (Gemini): {str(e)}")
            return "抱歉，生成綜合回答時發生錯誤（Gemini）。請稍後再試。"

    def _generate_answer_openai(self, question: str, context: str, question_analysis: Dict = None) -> str:
        """使用 OpenAI 生成回答（增強版）"""
        if not openai:
            return "本系統未安裝 openai 套件，請改用 Gemini 或安裝 openai。"
        
        # 根據問題複雜度調整 prompt
        if question_analysis and question_analysis.get('is_broad'):
            system_message = "你是一個專業的文檔問答助手，擅長處理廣泛性問題並提供全面、結構化的回答。"
            prompt = f"""
這是一個廣泛性問題，需要綜合分析多個來源的資訊。

重要指示：
1. 提供全面性的回答，組織清晰的結構
2. 使用 Markdown 格式美化回答
3. 先概述，再詳細說明，最後總結
4. 使用繁體中文回答

上下文資訊：
{context}

用戶問題：{question}

請提供全面且結構化的回答：
"""
        else:
            system_message = "你是一個專業的文檔問答助手，擅長根據提供的文檔內容回答問題。"
            prompt = f"""
根據提供的上下文資訊回答問題：

上下文資訊：
{context}

用戶問題：{question}

請提供準確且有幫助的回答：
"""
        
        try:
            response = openai.ChatCompletion.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating answer (OpenAI): {str(e)}")
            return "抱歉，生成回答時發生錯誤（OpenAI）。請稍後再試。"
    
    def _generate_comprehensive_answer_openai(self, question: str, context: str, sub_questions: List[str]) -> str:
        """為廣泛問題生成綜合回答（OpenAI）"""
        if not openai:
            return "本系統未安裝 openai 套件，請改用 Gemini 或安裝 openai。"
        
        prompt = f"""
原始問題：{question}

分解的子問題：
{chr(10).join([f"- {sq}" for sq in sub_questions])}

綜合上下文資訊：
{context}

請提供一個全面且結構化的回答，包括概述、詳細說明和總結。使用 Markdown 格式美化回答。
"""
        
        try:
            response = openai.ChatCompletion.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {
                        "role": "system", 
                        "content": "你是一個專業的文檔問答助手，擅長處理廣泛性問題並提供全面、結構化的回答。"
                    },
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2500,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error generating comprehensive answer (OpenAI): {str(e)}")
            return "抱歉，生成綜合回答時發生錯誤（OpenAI）。請稍後再試。"
    
    def _calculate_enhanced_confidence(self, relevant_docs: List[Dict], question_analysis: Dict) -> float:
        """計算增強的信心分數"""
        if not relevant_docs:
            return 0.0
        
        # 基礎信心分數
        base_confidence = self._calculate_confidence(relevant_docs)
        
        # 根據問題類型調整
        if question_analysis.get('is_broad'):
            # 廣泛問題：更多文檔通常意味著更好的覆蓋
            doc_count_bonus = min(0.2, len(relevant_docs) / 20)
            adjusted_confidence = base_confidence + doc_count_bonus
        else:
            # 具體問題：高相似度更重要
            top_similarity = 1 - relevant_docs[0].get('distance', 1) if relevant_docs else 0
            if top_similarity > 0.8:
                adjusted_confidence = base_confidence * 1.1  # 10% 加成
            else:
                adjusted_confidence = base_confidence
        
        return round(min(1.0, adjusted_confidence), 2)
    
    def _prepare_sources(self, relevant_docs: List[Dict]) -> List[Dict]:
        """準備來源資訊（增強版）"""
        sources = []
        seen_files = set()
        
        for doc in relevant_docs:
            filename = doc['metadata'].get('filename', '未知檔案')
            chunk_index = doc['metadata'].get('chunk_index', 0)
            total_chunks = doc['metadata'].get('total_chunks', 1)
            similarity = 1 - doc.get('distance', 1)
            
            if filename not in seen_files:
                sources.append({
                    'filename': filename,
                    'chunk_info': f"片段 {chunk_index + 1}/{total_chunks}",
                    'similarity': round(similarity, 2),
                    'relevance': 'high' if similarity > 0.8 else 'medium' if similarity > 0.6 else 'low'
                })
                seen_files.add(filename)
        
        # 按相似度排序
        sources.sort(key=lambda x: x['similarity'], reverse=True)
        return sources
    
    def _calculate_confidence(self, relevant_docs: List[Dict]) -> float:
        """計算基礎信心分數"""
        if not relevant_docs:
            return 0.0
        
        # 計算平均相似度
        similarities = [1 - doc.get('distance', 1) for doc in relevant_docs]
        avg_similarity = sum(similarities) / len(similarities)
        
        # 考慮結果數量（更多相關結果 = 更高信心）
        count_factor = min(1.0, len(relevant_docs) / Config.TOP_K)
        
        # 考慮最佳匹配
        best_similarity = max(similarities) if similarities else 0
        
        # 綜合計算
        confidence = (avg_similarity * 0.4 + best_similarity * 0.4 + count_factor * 0.2)
        
        return round(max(0.0, min(1.0, confidence)), 2)
    
    def get_available_documents(self) -> List[str]:
        """取得可用的文檔清單"""
        return self.vector_store.get_document_list()
    
    def get_retrieval_stats(self) -> Dict:
        """獲取檢索統計資訊"""
        try:
            total_docs = len(self.get_available_documents())
            total_chunks = len(self.vector_store.collection.get()['ids']) if hasattr(self.vector_store, 'collection') else 0
            
            return {
                'total_documents': total_docs,
                'total_chunks': total_chunks,
                'retrieval_config': {
                    'top_k': Config.TOP_K,
                    'max_top_k': Config.MAX_TOP_K,
                    'similarity_threshold': Config.SIMILARITY_THRESHOLD,
                    'adaptive_retrieval': Config.ADAPTIVE_RETRIEVAL,
                    'context_expansion': Config.CONTEXT_EXPANSION
                }
            }
        except Exception as e:
            print(f"Error getting retrieval stats: {e}")
            return {}