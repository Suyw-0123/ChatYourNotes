"""
智能檢索服務 - 實現 Context 擴展策略和資訊量自適應
"""

import re
from typing import List, Dict, Tuple
from src.config import Config
from src.vector_store import VectorStore


class SmartRetrievalService:
    def __init__(self):
        self.vector_store = VectorStore()
    
    def analyze_question_complexity(self, question: str) -> Dict:
        """分析問題複雜度和類型"""
        question_lower = question.lower()
        
        # 檢查是否為廣泛性問題
        is_broad = any(keyword in question_lower for keyword in Config.BROAD_QUESTION_KEYWORDS)
        
        # 計算問題長度和複雜度
        word_count = len(question.split())
        char_count = len(question)
        
        # 檢測問題類型
        question_types = []
        if any(word in question_lower for word in ['什麼', 'what', '是什麼', '定義']):
            question_types.append('definition')
        if any(word in question_lower for word in ['如何', 'how', '怎麼', '方法']):
            question_types.append('procedure')
        if any(word in question_lower for word in ['為什麼', 'why', '原因', '理由']):
            question_types.append('explanation')
        if any(word in question_lower for word in ['比較', 'compare', '差異', '不同']):
            question_types.append('comparison')
        if any(word in question_lower for word in ['列出', 'list', '有哪些', '包括']):
            question_types.append('enumeration')
        
        return {
            'is_broad': is_broad,
            'word_count': word_count,
            'char_count': char_count,
            'complexity_score': min(10, char_count / 10 + word_count / 5),
            'question_types': question_types
        }
    
    def decompose_broad_question(self, question: str) -> List[str]:
        """將廣泛問題分解為子問題"""
        analysis = self.analyze_question_complexity(question)
        
        if not analysis['is_broad']:
            return [question]
        
        # 基本分解策略
        sub_questions = []
        question_lower = question.lower()
        
        if '整篇' in question_lower or '全部' in question_lower:
            sub_questions.extend([
                "主要內容是什麼？",
                "重點概念有哪些？", 
                "結論是什麼？"
            ])
        
        if '詳細解釋' in question_lower:
            # 從原問題中提取關鍵詞
            keywords = self._extract_keywords(question)
            for keyword in keywords[:3]:  # 最多3個關鍵詞
                sub_questions.append(f"{keyword}是什麼？")
                sub_questions.append(f"{keyword}的詳細說明？")
        
        return sub_questions if sub_questions else [question]
    
    def adaptive_retrieval(self, question: str) -> List[Dict]:
        """自適應檢索策略"""
        analysis = self.analyze_question_complexity(question)
        
        # 根據問題複雜度調整檢索參數
        if analysis['is_broad'] or analysis['complexity_score'] > 7:
            # 複雜/廣泛問題：增加檢索數量，降低相似度閾值
            top_k = min(Config.MAX_TOP_K, Config.TOP_K * 3)
            threshold = Config.SIMILARITY_THRESHOLD * 0.8
        elif analysis['complexity_score'] < 3:
            # 簡單問題：減少檢索數量，提高相似度閾值
            top_k = max(Config.MIN_TOP_K, Config.TOP_K // 2)
            threshold = Config.SIMILARITY_THRESHOLD * 1.1
        else:
            # 一般問題：使用預設設定
            top_k = Config.TOP_K
            threshold = Config.SIMILARITY_THRESHOLD
        
        print(f"Adaptive retrieval: top_k={top_k}, threshold={threshold}, complexity={analysis['complexity_score']}")
        
        # 執行初始檢索
        initial_results = self.vector_store.search(question, top_k)
        
        # 過濾低相似度結果
        filtered_results = [
            doc for doc in initial_results 
            if (1 - doc.get('distance', 1)) >= threshold
        ]
        
        # 如果結果太少且是複雜問題，放寬條件重新檢索
        if len(filtered_results) < Config.MIN_TOP_K and analysis['is_broad']:
            print("Results too few for broad question, expanding retrieval...")
            expanded_results = self.vector_store.search(question, Config.MAX_TOP_K)
            filtered_results = expanded_results[:Config.TOP_K * 2]
        
        # Context 擴展
        if Config.CONTEXT_EXPANSION:
            filtered_results = self._expand_context(filtered_results)
        
        return filtered_results
    
    def _expand_context(self, initial_results: List[Dict]) -> List[Dict]:
        """擴展上下文 - 尋找相鄰片段"""
        expanded_results = list(initial_results)
        
        for doc in initial_results:
            filename = doc['metadata'].get('filename')
            chunk_index = doc['metadata'].get('chunk_index', 0)
            
            if filename and chunk_index is not None:
                # 嘗試獲取前後相鄰的片段
                for offset in [-1, 1]:
                    neighbor_id = f"{filename}_chunk_{chunk_index + offset}"
                    neighbor = self._get_chunk_by_id(neighbor_id)
                    if neighbor and neighbor not in expanded_results:
                        # 檢查是否內容相關（簡單的重疊檢查）
                        if self._is_content_related(doc['content'], neighbor['content']):
                            expanded_results.append(neighbor)
        
        # 按原始相似度排序
        return expanded_results
    
    def _get_chunk_by_id(self, chunk_id: str) -> Dict:
        """根據 ID 獲取特定片段"""
        return self.vector_store.get_chunk_by_id(chunk_id)
    
    def _is_content_related(self, content1: str, content2: str) -> bool:
        """檢查兩個內容片段是否相關"""
        # 簡單的關鍵詞重疊檢查
        words1 = set(content1.lower().split())
        words2 = set(content2.lower().split())
        
        # 計算交集比例
        intersection = words1.intersection(words2)
        union = words1.union(words2)
        
        similarity = len(intersection) / len(union) if union else 0
        return similarity > 0.3  # 30% 以上重疊認為相關
    
    def _extract_keywords(self, text: str) -> List[str]:
        """提取關鍵詞"""
        # 移除標點符號並分詞
        cleaned_text = re.sub(r'[^\w\s]', ' ', text)
        words = cleaned_text.split()
        
        # 過濾停用詞（簡化版）
        stop_words = {
            '的', '了', '是', '在', '有', '和', '與', '或', '但', '而', '也', '都', '很', '更', '最',
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with'
        }
        
        keywords = [word for word in words if word.lower() not in stop_words and len(word) > 1]
        
        # 返回前5個關鍵詞
        return keywords[:5]
    
    def manage_token_budget(self, context_parts: List[str], question: str) -> str:
        """管理 Token 預算，確保不超過限制"""
        # 簡化的 token 計算（1 token ≈ 4 字符）
        question_tokens = len(question) // 4
        available_tokens = Config.MAX_CONTEXT_TOKENS - question_tokens - 500  # 保留回答空間
        
        if available_tokens <= 0:
            return "問題過長，請簡化問題。"
        
        # 按優先級排序並截斷
        current_tokens = 0
        selected_parts = []
        
        for part in context_parts:
            part_tokens = len(part) // 4
            if current_tokens + part_tokens <= available_tokens:
                selected_parts.append(part)
                current_tokens += part_tokens
            else:
                # 如果還有空間，截斷這一部分
                remaining_chars = (available_tokens - current_tokens) * 4
                if remaining_chars > 100:  # 至少保留100字符
                    truncated_part = part[:remaining_chars] + "...[內容截斷]"
                    selected_parts.append(truncated_part)
                break
        
        print(f"Token budget: used {current_tokens}/{available_tokens} tokens")
        return "\n\n".join(selected_parts)
