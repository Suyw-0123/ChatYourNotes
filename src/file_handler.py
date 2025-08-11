import os
import shutil
from werkzeug.utils import secure_filename
from src.config import Config

class FileHandler:
    def __init__(self):
        Config.ensure_directories()
        self.allowed_extensions = {'pdf'}
    
    def allowed_file(self, filename):
        """檢查檔案副檔名是否被允許"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in self.allowed_extensions
    
    def save_pdf(self, file):
        """儲存上傳的 PDF 檔案"""
        if file and self.allowed_file(file.filename):
            filename = secure_filename(file.filename)
            file_path = os.path.join(Config.PDF_DIR, filename)
            
            # 如果檔案已存在，產生新的檔名
            counter = 1
            original_name, extension = os.path.splitext(filename)
            while os.path.exists(file_path):
                new_filename = f"{original_name}_{counter}{extension}"
                file_path = os.path.join(Config.PDF_DIR, new_filename)
                filename = new_filename
                counter += 1
            
            file.save(file_path)
            return file_path, filename
        return None, None
    
    def get_pdf_list(self):
        """取得所有已上傳的 PDF 檔案清單"""
        pdf_files = []
        if os.path.exists(Config.PDF_DIR):
            for filename in os.listdir(Config.PDF_DIR):
                if filename.lower().endswith('.pdf'):
                    pdf_files.append(filename)
        return pdf_files
    
    def delete_pdf(self, filename):
        """刪除 PDF 檔案及其相關資料"""
        try:
            # 刪除 PDF
            pdf_path = os.path.join(Config.PDF_DIR, filename)
            if os.path.exists(pdf_path):
                os.remove(pdf_path)
            
            # 刪除對應的 OCR 文字檔
            ocr_filename = os.path.splitext(filename)[0] + '.txt'
            ocr_path = os.path.join(Config.OCR_DIR, ocr_filename)
            if os.path.exists(ocr_path):
                os.remove(ocr_path)
            
            # 刪除對應的摘要檔
            summary_path = os.path.join(Config.SUMMARY_DIR, ocr_filename)
            if os.path.exists(summary_path):
                os.remove(summary_path)
            
            return True
        except Exception as e:
            print(f"Error deleting file {filename}: {str(e)}")
            return False