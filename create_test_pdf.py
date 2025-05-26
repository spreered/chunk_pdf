import fitz  # PyMuPDF

def create_test_pdf(output_path):
    """
    創建一個測試用的 PDF 檔案，包含多個章節和目錄
    
    Args:
        output_path (str): 輸出 PDF 檔案的路徑
    """
    # 創建新的 PDF 文件
    doc = fitz.open()
    
    # 添加頁面和內容
    for i in range(1, 11):
        page = doc.new_page()
        text = f"第 {i} 頁的內容"
        page.insert_text((50, 50), text, fontsize=12)
    
    # 創建目錄結構
    toc = [
        [1, "第一章", 1],
        [2, "第一章第一節", 2],
        [2, "第一章第二節", 3],
        [1, "第二章", 4],
        [2, "第二章第一節", 5],
        [2, "第二章第二節", 6],
        [1, "第三章", 7],
        [2, "第三章第一節", 8],
        [2, "第三章第二節", 9],
        [1, "附錄", 10]
    ]
    
    # 設置目錄
    doc.set_toc(toc)
    
    # 保存 PDF
    doc.save(output_path)
    doc.close()
    
    print(f"測試 PDF 已創建: {output_path}")

if __name__ == "__main__":
    output_path = "test_document.pdf"
    create_test_pdf(output_path)
