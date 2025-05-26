import os
import re
import fitz  # PyMuPDF

class PDFChunker:
    """
    核心類別，用於處理 PDF 檔案的加載、目錄提取和分塊功能
    """
    
    def __init__(self, pdf_path=None):
        """
        初始化 PDFChunker 實例
        
        Args:
            pdf_path (str, optional): PDF 檔案的路徑
        """
        self.pdf_path = pdf_path
        self.doc = None
        self.toc = None
        self.toc_tree = None
        
    def load_pdf(self, pdf_path=None):
        """
        加載 PDF 檔案
        
        Args:
            pdf_path (str, optional): PDF 檔案的路徑，如果提供則更新實例的 pdf_path
            
        Returns:
            bool: 是否成功加載 PDF
            
        Raises:
            ValueError: 如果 PDF 路徑無效或檔案無法讀取
        """
        if pdf_path:
            self.pdf_path = pdf_path
            
        if not self.pdf_path:
            raise ValueError("PDF 路徑未提供")
            
        try:
            self.doc = fitz.open(self.pdf_path)
            return True
        except Exception as e:
            raise ValueError(f"無法讀取 PDF 檔案: {str(e)}")
    
    def extract_toc(self):
        """
        從 PDF 提取目錄 (Table of Contents)
        
        Returns:
            list: 目錄項目列表，每個項目包含 level, title, page 等資訊
            
        Raises:
            ValueError: 如果 PDF 尚未加載
        """
        if not self.doc:
            raise ValueError("PDF 尚未加載，請先呼叫 load_pdf()")
            
        self.toc = self.doc.get_toc(simple=False)
        
        if not self.toc:
            return []
            
        # 將目錄轉換為更易於處理的格式
        formatted_toc = []
        for item in self.toc:
            level, title, page = item[:3]
            formatted_toc.append({
                "level": level,
                "title": title,
                "page": page,
                "selected": False
            })
            
        self.toc = formatted_toc
        return self.toc
    
    def build_toc_tree(self):
        """
        將線性目錄轉換為樹狀結構，便於處理父子關係
        
        Returns:
            list: 樹狀結構的目錄
            
        Raises:
            ValueError: 如果目錄尚未提取
        """
        if not self.toc:
            raise ValueError("目錄尚未提取，請先呼叫 extract_toc()")
            
        root = []
        stack = [(0, root)]  # (level, children_list)
        
        for item in self.toc:
            current_level = item["level"]
            
            # 找到適當的父節點
            while stack and stack[-1][0] >= current_level:
                stack.pop()
                
            if not stack:
                stack.append((0, root))
                
            parent_level, parent_children = stack[-1]
            
            # 創建新節點並添加到父節點的子節點列表中
            new_node = item.copy()
            new_node["children"] = []
            parent_children.append(new_node)
            
            # 將新節點加入堆疊
            stack.append((current_level, new_node["children"]))
            
        self.toc_tree = root
        return root
    
    def determine_chunk_ranges(self, selections):
        """
        根據用戶選擇確定每個分塊的頁面範圍
        
        Args:
            selections (list): 用戶選擇的目錄項目列表，每個項目應包含 level, title, page 和 selected 屬性
            
        Returns:
            list: 分塊範圍列表，每個範圍包含 title, start_page, end_page
            
        Raises:
            ValueError: 如果目錄尚未提取
        """
        if not self.toc:
            raise ValueError("目錄尚未提取，請先呼叫 extract_toc()")
            
        # 根據選擇確定分塊範圍
        chunks = []
        selected_indices = [i for i, item in enumerate(selections) if item["selected"]]
        
        for idx in selected_indices:
            item = selections[idx]
            start_page = item["page"]
            title = item["title"]
            level = item["level"]
            
            # 確定結束頁面
            end_page = self.doc.page_count  # 預設為 PDF 的最後一頁
            
            # 尋找下一個同級或更高級的目錄項目
            for next_idx in range(idx + 1, len(selections)):
                next_item = selections[next_idx]
                if next_item["level"] <= level:
                    end_page = next_item["page"] - 1
                    break
            
            # 確保頁面範圍有效
            start_page = max(1, start_page)
            end_page = max(start_page, min(end_page, self.doc.page_count))
            
            chunks.append({
                "title": title,
                "start_page": start_page,
                "end_page": end_page
            })
            
        return chunks
    
    def create_chunks(self, chunks, output_dir=None):
        """
        根據確定的範圍創建 PDF 分塊
        
        Args:
            chunks (list): 分塊範圍列表，每個範圍包含 title, start_page, end_page
            output_dir (str, optional): 輸出目錄，如果未提供則使用原始 PDF 所在目錄
            
        Returns:
            list: 創建的分塊 PDF 檔案路徑列表
            
        Raises:
            ValueError: 如果 PDF 尚未加載
        """
        if not self.doc:
            raise ValueError("PDF 尚未加載，請先呼叫 load_pdf()")
            
        # 確保輸出目錄有效
        if not output_dir:
            output_dir = os.path.dirname(self.pdf_path)
            if not output_dir:  # 如果 pdf_path 只是檔案名稱而沒有目錄部分
                output_dir = os.getcwd()
            
        # 確保輸出目錄存在
        os.makedirs(output_dir, exist_ok=True)
        
        # 獲取原始檔案名稱（不含副檔名）
        original_filename = os.path.splitext(os.path.basename(self.pdf_path))[0]
        
        created_files = []
        
        for chunk in chunks:
            # 清理標題以用於檔案名稱
            sanitized_title = self._sanitize_filename(chunk["title"])
            output_filename = f"{original_filename}_{sanitized_title}.pdf"
            output_path = os.path.join(output_dir, output_filename)
            
            # 創建新的 PDF 文件
            new_doc = fitz.open()
            
            # PyMuPDF 頁面是從 0 開始索引的，而 ToC 頁面通常是從 1 開始索引的
            start_idx = chunk["start_page"] - 1
            end_idx = chunk["end_page"] - 1
            
            # 確保索引有效
            start_idx = max(0, start_idx)
            end_idx = min(self.doc.page_count - 1, end_idx)
            
            # 插入頁面
            new_doc.insert_pdf(self.doc, from_page=start_idx, to_page=end_idx)
            
            # 保存新的 PDF
            new_doc.save(output_path)
            new_doc.close()
            
            created_files.append(output_path)
            
        return created_files
    
    def _sanitize_filename(self, filename):
        """
        清理字符串以用作有效的檔案名稱
        
        Args:
            filename (str): 原始字符串
            
        Returns:
            str: 清理後的字符串
        """
        # 移除或替換無效的檔案名稱字符
        invalid_chars = r'[\\/*?:"<>|]'
        sanitized = re.sub(invalid_chars, "_", filename)
        
        # 移除前後空格
        sanitized = sanitized.strip()
        
        # 確保檔案名稱不為空
        if not sanitized:
            sanitized = "unnamed_section"
            
        # 限制檔案名稱長度
        if len(sanitized) > 100:
            sanitized = sanitized[:100]
            
        return sanitized
    
    def close(self):
        """
        關閉 PDF 文件並釋放資源
        """
        if self.doc:
            self.doc.close()
            self.doc = None
