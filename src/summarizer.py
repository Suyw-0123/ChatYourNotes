import os
import openai
from src.config import Config

class Summarizer:
    def __init__(self):
        openai.api_key = Config.OPENAI_API_KEY
    
    def create_summary(self, text, filename):
        """使用 OpenAI GPT 創建文檔摘要"""
        try:
            print(f"Creating summary for {filename}...")
            
            # 如果文本太長，先進行分段摘要
            if len(text) > 8000:  # 大約 2000 個 tokens
                summary = self._create_long_text_summary(text)
            else:
                summary = self._create_short_text_summary(text)
            
            # 儲存摘要
            summary_filename = os.path.splitext(filename)[0] + '.txt'
            summary_path = os.path.join(Config.SUMMARY_DIR, summary_filename)
            
            with open(summary_path, 'w', encoding='utf-8') as f:
                f.write(summary)
            
            print(f"Summary created and saved to {summary_path}")
            return summary_path, summary
            
        except Exception as e:
            print(f"Error creating summary for {filename}: {str(e)}")
            return None, None
    
    def _create_short_text_summary(self, text):
        """為短文本創建摘要"""
        prompt = f"""
        請為以下文檔創建一個詳細的摘要，包含：
        1. 主要主題和內容概述
        2. 重要的關鍵點
        3. 結論或重要發現
        
        文檔內容：
        {text}
        
        請用繁體中文回答，摘要應該詳細但簡潔。
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一個專業的文檔摘要專家，擅長提取重要資訊並創建結構化摘要。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1000,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error calling OpenAI API: {str(e)}")
            return "摘要生成失敗"
    
    def _create_long_text_summary(self, text):
        """為長文本創建摘要（分段處理）"""
        # 將長文本分成較小的段落
        chunks = self._split_text_into_chunks(text, 6000)
        chunk_summaries = []
        
        for i, chunk in enumerate(chunks):
            print(f"Summarizing chunk {i+1}/{len(chunks)}...")
            chunk_summary = self._create_short_text_summary(chunk)
            chunk_summaries.append(chunk_summary)
        
        # 將所有段落摘要合併成最終摘要
        combined_summary = "\n\n".join(chunk_summaries)
        final_summary = self._create_final_summary(combined_summary)
        
        return final_summary
    
    def _create_final_summary(self, combined_summary):
        """創建最終摘要"""
        prompt = f"""
        以下是一個長文檔的分段摘要，請將這些摘要整合成一個完整、連貫的最終摘要：
        
        {combined_summary}
        
        請用繁體中文創建一個結構化的最終摘要，包含主要主題、重點和結論。
        """
        
        try:
            response = openai.ChatCompletion.create(
                model=Config.OPENAI_MODEL,
                messages=[
                    {"role": "system", "content": "你是一個專業的文檔摘要專家，擅長整合多個摘要成為連貫的最終摘要。"},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.3
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            print(f"Error creating final summary: {str(e)}")
            return combined_summary  # 如果失敗，返回合併的摘要
    
    def _split_text_into_chunks(self, text, chunk_size):
        """將文本分割成指定大小的塊"""
        chunks = []
        for i in range(0, len(text), chunk_size):
            chunks.append(text[i:i + chunk_size])
        return chunks