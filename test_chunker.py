import os
import sys
import argparse
from pdf_chunker import PDFChunker

def main():
    """
    測試 PDF 分割工具的核心功能
    """
    # 解析命令行參數
    parser = argparse.ArgumentParser(description='測試 PDF 分割工具')
    parser.add_argument('pdf_path', help='PDF 檔案的路徑')
    parser.add_argument('--output-dir', help='輸出目錄路徑 (可選)')
    args = parser.parse_args()
    
    pdf_path = args.pdf_path
    output_dir = args.output_dir
    
    # 檢查 PDF 檔案是否存在
    if not os.path.exists(pdf_path):
        print(f"錯誤: 找不到 PDF 檔案 '{pdf_path}'")
        return 1
    
    try:
        # 初始化 PDFChunker
        chunker = PDFChunker(pdf_path)
        
        # 加載 PDF
        print(f"正在加載 PDF: {pdf_path}")
        chunker.load_pdf()
        
        # 提取目錄
        print("正在提取目錄...")
        toc = chunker.extract_toc()
        
        if not toc:
            print("警告: PDF 中沒有找到目錄")
            chunker.close()
            return 1
        
        # 顯示提取的目錄
        print("\n目錄結構:")
        for item in toc:
            indent = "  " * (item["level"] - 1)
            print(f"{indent}- {item['title']} (頁面: {item['page']})")
        
        # 模擬用戶選擇 (這裡我們選擇第一個和第三個目錄項目)
        if len(toc) >= 1:
            toc[0]["selected"] = True
        if len(toc) >= 3:
            toc[2]["selected"] = True
        
        print("\n已選擇的目錄項目:")
        for item in toc:
            if item["selected"]:
                print(f"- {item['title']} (頁面: {item['page']})")
        
        # 確定分塊範圍
        print("\n正在確定分塊範圍...")
        chunks = chunker.determine_chunk_ranges(toc)
        
        print("\n分塊範圍:")
        for chunk in chunks:
            print(f"- {chunk['title']}: 頁面 {chunk['start_page']} 到 {chunk['end_page']}")
        
        # 創建分塊
        print("\n正在創建分塊...")
        created_files = chunker.create_chunks(chunks, output_dir)
        
        print("\n創建的分塊檔案:")
        for file_path in created_files:
            print(f"- {file_path}")
        
        # 關閉 PDF
        chunker.close()
        
        print("\n處理完成!")
        return 0
        
    except Exception as e:
        print(f"錯誤: {str(e)}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
