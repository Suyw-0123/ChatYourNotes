import os
import PyPDF2
import pytesseract
from pdf2image import convert_from_path
from PIL import Image
from src.config import Config

class OCRReader:
    def __init__(self):
        # 設定 Tesseract 路徑（Windows 用戶可能需要）
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def extract_text_from_pdf(self, pdf_path):
        """從 PDF 中提取文字，先嘗試直接提取，再使用 OCR"""
        try:
            # 方法1：嘗試直接從 PDF 提取文字
            text = self._extract_text_directly(pdf_path)
            
            # 如果直接提取的文字太少，使用 OCR
            if len(text.strip()) < 100:
                print(f"Direct extraction yielded little text, using OCR...")
                text = self._extract_text_with_ocr(pdf_path)
            
            return text
        except Exception as e:
            print(f"Error extracting text from PDF: {str(e)}")
            return ""
    
    def _extract_text_directly(self, pdf_path):
        """直接從 PDF 提取文字"""
        text = ""
        try:
            with open(pdf_path, 'rb') as file:
                pdf_reader = PyPDF2.PdfReader(file)
                for page_num in range(len(pdf_reader.pages)):
                    page = pdf_reader.pages[page_num]
                    text += page.extract_text() + "\n"
        except Exception as e:
            print(f"Error in direct text extraction: {str(e)}")
        return text
    
    def _extract_text_with_ocr(self, pdf_path):
        """使用 OCR 從 PDF 提取文字"""
        text = ""
        try:
            # 將 PDF 轉換為圖片
            pages = convert_from_path(pdf_path, dpi=200)
            
            for i, page in enumerate(pages):
                print(f"Processing page {i+1}/{len(pages)} with OCR...")
                # 使用 Tesseract 進行 OCR
                page_text = pytesseract.image_to_string(page, lang='chi_tra+eng')
                text += f"\n--- Page {i+1} ---\n{page_text}\n"
                
        except Exception as e:
            print(f"Error in OCR extraction: {str(e)}")
        
        return text
    
    def process_pdf(self, pdf_path, filename):
        """處理 PDF 並儲存提取的文字"""
        try:
            print(f"Starting OCR processing for {filename}...")
            
            # 提取文字
            text = self.extract_text_from_pdf(pdf_path)
            
            if not text.strip():
                raise Exception("No text could be extracted from the PDF")
            
            # 儲存提取的文字
            ocr_filename = os.path.splitext(filename)[0] + '.txt'
            ocr_path = os.path.join(Config.OCR_DIR, ocr_filename)
            
            with open(ocr_path, 'w', encoding='utf-8') as f:
                f.write(text)
            
            print(f"OCR processing completed. Text saved to {ocr_path}")
            return ocr_path, text
            
        except Exception as e:
            print(f"Error processing PDF {filename}: {str(e)}")
            return None, None