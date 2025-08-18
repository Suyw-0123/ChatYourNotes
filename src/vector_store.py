import os
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import numpy as np
from typing import List, Dict
from src.config import Config

class VectorStore:
    def __init__(self):
        # 初始化 ChromaDB
        self.client = chromadb.PersistentClient(
            path=Config.VECTOR_STORE_DIR,
            settings=Settings(anonymized_telemetry=False)
        )
        
        # 初始化嵌入模型
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
        
        # 取得或創建集合
        self.collection = self.client.get_or_create_collection(
            name="pdf_documents",
            metadata={"hnsw:space": "cosine"}
        )
    
    def add_document(self, text: str, filename: str):
        """將文檔添加到向量資料庫"""
        try:
            print(f"Adding document {filename} to vector store...")
            
            # 將文本分塊
            chunks = self._split_text_into_chunks(text, Config.CHUNK_SIZE, Config.CHUNK_OVERLAP)
            
            # 生成嵌入向量
            embeddings = self.embedding_model.encode(chunks).tolist()
            
            # 生成文檔 IDs
            doc_ids = [f"{filename}_chunk_{i}" for i in range(len(chunks))]
            
            # 準備元數據
            metadatas = [
                {
                    "filename": filename,
                    "chunk_index": i,
                    "total_chunks": len(chunks)
                }
                for i in range(len(chunks))
            ]
            
            # 添加到 ChromaDB
            self.collection.add(
                documents=chunks,
                embeddings=embeddings,
                metadatas=metadatas,
                ids=doc_ids
            )
            
            print(f"Successfully added {len(chunks)} chunks from {filename}")
            return True
            
        except Exception as e:
            print(f"Error adding document {filename} to vector store: {str(e)}")
            return False
    
    def search(self, query: str, top_k: int = None) -> List[Dict]:
        """搜索相關文檔片段（增強版）"""
        if top_k is None:
            top_k = Config.TOP_K
        
        try:
            # 生成查詢的嵌入向量
            query_embedding = self.embedding_model.encode([query]).tolist()
            
            # 搜索
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=top_k
            )
            
            # 格式化結果
            formatted_results = []
            if results['documents'] and len(results['documents']) > 0:
                for i in range(len(results['documents'][0])):
                    formatted_results.append({
                        'content': results['documents'][0][i],
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0,
                        'id': results['ids'][0][i] if results['ids'] else f'doc_{i}'
                    })
            
            return formatted_results
            
        except Exception as e:
            print(f"Error searching vector store: {str(e)}")
            return []
    
    def get_chunk_by_id(self, chunk_id: str) -> Dict:
        """根據 ID 獲取特定片段"""
        try:
            results = self.collection.get(ids=[chunk_id])
            if results['documents'] and len(results['documents']) > 0:
                return {
                    'content': results['documents'][0],
                    'metadata': results['metadatas'][0] if results['metadatas'] else {},
                    'distance': 0,  # 直接獲取的片段設為高相似度
                    'id': chunk_id
                }
        except Exception as e:
            print(f"Error getting chunk {chunk_id}: {e}")
        return None
    
    def get_adjacent_chunks(self, filename: str, chunk_index: int, window_size: int = 1) -> List[Dict]:
        """獲取相鄰的文檔片段"""
        try:
            adjacent_chunks = []
            
            for offset in range(-window_size, window_size + 1):
                if offset == 0:  # 跳過當前片段
                    continue
                    
                target_index = chunk_index + offset
                if target_index < 0:  # 跳過負索引
                    continue
                    
                chunk_id = f"{filename}_chunk_{target_index}"
                chunk = self.get_chunk_by_id(chunk_id)
                
                if chunk:
                    adjacent_chunks.append(chunk)
            
            return adjacent_chunks
            
        except Exception as e:
            print(f"Error getting adjacent chunks: {e}")
            return []
    
    def delete_document(self, filename: str):
        """從向量資料庫中刪除文檔"""
        try:
            # 找到所有相關的文檔塊
            results = self.collection.get(
                where={"filename": filename}
            )
            
            if results['ids']:
                # 刪除所有相關的塊
                self.collection.delete(ids=results['ids'])
                print(f"Deleted {len(results['ids'])} chunks for {filename}")
                return True
            
            return True
            
        except Exception as e:
            print(f"Error deleting document {filename} from vector store: {str(e)}")
            return False
    
    def get_document_list(self) -> List[str]:
        """取得向量資料庫中所有文檔的清單"""
        try:
            results = self.collection.get()
            filenames = set()
            
            if results['metadatas']:
                for metadata in results['metadatas']:
                    if 'filename' in metadata:
                        filenames.add(metadata['filename'])
            
            return list(filenames)
            
        except Exception as e:
            print(f"Error getting document list: {str(e)}")
            return []
    
    def _split_text_into_chunks(self, text: str, chunk_size: int, chunk_overlap: int) -> List[str]:
        """將文本分割成重疊的塊"""
        chunks = []
        start = 0
        
        while start < len(text):
            # 計算結束位置
            end = start + chunk_size
            
            if end >= len(text):
                # 最後一塊
                chunks.append(text[start:])
                break
            
            # 尋找適當的分割點（避免在單詞中間分割）
            split_end = end
            for i in range(end, max(start, end - 100), -1):
                if text[i] in [' ', '\n', '\t', '。', '！', '？', '.', '!', '?']:
                    split_end = i + 1
                    break
            
            chunks.append(text[start:split_end])
            start = split_end - chunk_overlap if split_end > chunk_overlap else split_end
        
        return [chunk.strip() for chunk in chunks if chunk.strip()]