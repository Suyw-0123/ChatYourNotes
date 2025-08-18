#!/usr/bin/env python3
"""
測試智能檢索功能
"""

import sys
import os

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.qa_service import QAService
from src.smart_retrieval import SmartRetrievalService

def test_question_analysis():
    """測試問題分析功能"""
    print("=== 測試問題分析功能 ===")
    
    smart_retrieval = SmartRetrievalService()
    
    test_questions = [
        "什麼是機器學習？",
        "請詳細解釋整篇文件的內容",
        "如何實現深度學習模型？",
        "比較不同演算法的優缺點",
        "列出所有重要概念"
    ]
    
    for question in test_questions:
        analysis = smart_retrieval.analyze_question_complexity(question)
        print(f"\n問題: {question}")
        print(f"分析結果: {analysis}")

def test_question_decomposition():
    """測試問題分解功能"""
    print("\n=== 測試問題分解功能 ===")
    
    smart_retrieval = SmartRetrievalService()
    
    broad_questions = [
        "請解釋整篇筆記的內容",
        "詳細說明所有重要概念",
        "給我一個完整的總結"
    ]
    
    for question in broad_questions:
        sub_questions = smart_retrieval.decompose_broad_question(question)
        print(f"\n原問題: {question}")
        print(f"分解後的子問題:")
        for i, sq in enumerate(sub_questions, 1):
            print(f"  {i}. {sq}")

def test_adaptive_qa():
    """測試自適應問答功能"""
    print("\n=== 測試自適應問答功能 ===")
    
    qa_service = QAService()
    
    test_questions = [
        "什麼是PDF？",  # 簡單問題
        "請詳細解釋文件中提到的所有重要概念",  # 廣泛問題
        "如何處理OCR文字識別？"  # 中等複雜度問題
    ]
    
    for question in test_questions:
        print(f"\n問題: {question}")
        try:
            result = qa_service.answer_question(question)
            print(f"回答: {result['answer'][:200]}...")
            print(f"信心度: {result['confidence']}")
            print(f"檢索文檔數: {result['retrieved_docs']}")
            
            if 'question_analysis' in result:
                print(f"問題分析: {result['question_analysis']}")
            
            if 'sub_questions' in result:
                print(f"子問題: {result['sub_questions']}")
                
        except Exception as e:
            print(f"錯誤: {e}")

def test_retrieval_stats():
    """測試檢索統計功能"""
    print("\n=== 測試檢索統計功能 ===")
    
    qa_service = QAService()
    
    try:
        stats = qa_service.get_retrieval_stats()
        print(f"檢索統計: {stats}")
    except Exception as e:
        print(f"錯誤: {e}")

if __name__ == "__main__":
    print("開始測試智能檢索功能...")
    
    # 確保目錄存在
    from src.config import Config
    Config.ensure_directories()
    
    try:
        test_question_analysis()
        test_question_decomposition()
        test_retrieval_stats()
        
        # 只有在有文檔的情況下才測試QA
        qa_service = QAService()
        if qa_service.get_available_documents():
            test_adaptive_qa()
        else:
            print("\n注意: 沒有可用的文檔，跳過QA測試")
            print("請先上傳一些PDF文件到系統中")
        
    except Exception as e:
        print(f"測試過程中發生錯誤: {e}")
        import traceback
        traceback.print_exc()
    
    print("\n測試完成！")
