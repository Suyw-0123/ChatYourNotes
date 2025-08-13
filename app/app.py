import os
import sys
from flask import Flask, render_template, request, jsonify, redirect, url_for, flash
from werkzeug.utils import secure_filename
import json

# 添加專案根目錄到 Python 路徑
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config import Config
from src.file_handler import FileHandler
from src.ocr_reader import OCRReader
from src.summarizer import Summarizer
from src.vector_store import VectorStore
from src.qa_service import QAService


app = Flask(__name__)
app.secret_key = 'your-secret-key-here'  # 請更改為安全的密鑰
# 設定最大上傳檔案大小（32MB）
app.config['MAX_CONTENT_LENGTH'] = 32 * 1024 * 1024

# 初始化服務
file_handler = FileHandler()
ocr_reader = OCRReader()
summarizer = Summarizer()
vector_store = VectorStore()
qa_service = QAService()

@app.route('/')
def index():
    """首頁，自動補處理所有未完成的 PDF"""
    pdf_files = file_handler.get_pdf_list()
    available_docs = set(qa_service.get_available_documents())
    errors = []
    # 自動補處理未完成的 PDF
    for filename in pdf_files:
        if filename not in available_docs:
            try:
                file_path = os.path.join(Config.PDF_DIR, filename)
                # OCR
                ocr_path, text = ocr_reader.process_pdf(file_path, filename)
                if not text:
                    raise Exception('OCR 文字提取失敗')
                # 摘要
                summary_path, summary = summarizer.create_summary(text, filename)
                if not summary:
                    raise Exception('摘要生成失敗')
                # 向量化
                success = vector_store.add_document(text, filename)
                if not success:
                    raise Exception('向量資料庫處理失敗')
                available_docs.add(filename)
            except Exception as e:
                error_msg = f"檔案 {filename} 處理失敗：{str(e)}"
                print(error_msg)
                errors.append(error_msg)
    # 顯示所有錯誤
    for msg in errors:
        flash(msg, 'danger')
    return render_template('index.html', pdf_files=pdf_files, available_docs=available_docs)

@app.route('/upload', methods=['POST'])
def upload_file():
    print("[DEBUG] /upload 路由被呼叫")
    """處理 PDF 上傳，並加強錯誤提示"""
    try:
        if 'file' not in request.files:
            flash('沒有選擇檔案', 'danger')
            return redirect(request.url)

        file = request.files['file']

        if file.filename == '':
            flash('沒有選擇檔案', 'danger')
            return redirect(request.url)

        if file and file_handler.allowed_file(file.filename):
            # 1. 儲存 PDF 檔案
            file_path, filename = file_handler.save_pdf(file)
            if not file_path:
                flash('檔案儲存失敗', 'danger')
                return redirect(url_for('index'))
            try:
                # 2. OCR 處理
                ocr_path, text = ocr_reader.process_pdf(file_path, filename)
                if not text:
                    raise Exception('OCR 文字提取失敗')
                # 3. 生成摘要
                summary_path, summary = summarizer.create_summary(text, filename)
                if not summary:
                    raise Exception('摘要生成失敗')
                # 4. 添加到向量資料庫
                success = vector_store.add_document(text, filename)
                if success:
                    flash(f'檔案 {filename} 上傳並處理成功！', 'success')
                else:
                    raise Exception('向量資料庫處理失敗')
            except Exception as e:
                flash(f'檔案 {filename} 處理失敗：{str(e)}', 'danger')
        else:
            flash('不支援的檔案格式，請上傳 PDF 檔案', 'danger')

        return redirect(url_for('index'))

    except Exception as e:
        flash(f'處理檔案時發生錯誤：{str(e)}', 'danger')
        return redirect(url_for('index'))

@app.route('/ask', methods=['POST'])
def ask_question():
    """處理問答請求"""
    try:
        data = request.get_json()
        question = data.get('question', '').strip()
        
        if not question:
            return jsonify({
                'success': False,
                'error': '問題不能為空'
            })
        
        # 使用 QA 服務回答問題
        result = qa_service.answer_question(question)
        
        return jsonify({
            'success': True,
            'answer': result['answer'],
            'sources': result['sources'],
            'confidence': result['confidence'],
            'retrieved_docs': result.get('retrieved_docs', 0)
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'處理問題時發生錯誤：{str(e)}'
        })

@app.route('/delete/<filename>', methods=['POST'])
def delete_file(filename):
    """刪除檔案"""
    try:
        # 從文件系統刪除
        if file_handler.delete_pdf(filename):
            # 從向量資料庫刪除
            vector_store.delete_document(filename)
            flash(f'檔案 {filename} 已成功刪除')
        else:
            flash(f'刪除檔案 {filename} 失敗')
            
    except Exception as e:
        flash(f'刪除檔案時發生錯誤：{str(e)}')
    
    return redirect(url_for('index'))

@app.route('/api/documents', methods=['GET'])
def get_documents():
    """取得文檔清單 API"""
    try:
        pdf_files = file_handler.get_pdf_list()
        vector_docs = qa_service.get_available_documents()
        
        return jsonify({
            'success': True,
            'pdf_files': pdf_files,
            'vector_docs': vector_docs
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        })

if __name__ == '__main__':
    # 確保所有目錄都存在
    Config.ensure_directories()
    app.run(debug=True, host='0.0.0.0', port=5000)