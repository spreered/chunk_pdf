import os
import sys
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                              QLabel, QPushButton, QFileDialog, QCheckBox, QScrollArea, 
                              QFrame, QMessageBox, QLineEdit, QGroupBox)
from PySide6.QtCore import Qt, Signal
from pdf_chunker import PDFChunker

class PDFChunkerApp(QMainWindow):
    """
    PDF 分割工具的 GUI 應用程式
    """
    
    def __init__(self):
        """
        初始化 GUI 應用程式
        """
        super().__init__()
        
        self.chunker = None
        self.toc_items = []
        self.checkboxes = []
        
        self.init_ui()
        
    def init_ui(self):
        """
        初始化使用者界面
        """
        self.setWindowTitle("PDF 分割工具")
        self.setGeometry(100, 100, 800, 600)
        self.setMinimumSize(600, 400)
        
        # 主要 widget 和佈局
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        
        # 檔案選擇區域
        file_group = QGroupBox("PDF 檔案選擇")
        file_layout = QHBoxLayout()
        
        self.file_path_label = QLineEdit()
        self.file_path_label.setReadOnly(True)
        file_layout.addWidget(QLabel("檔案路徑:"))
        file_layout.addWidget(self.file_path_label)
        
        self.select_file_btn = QPushButton("選擇 PDF")
        self.select_file_btn.clicked.connect(self.select_pdf)
        file_layout.addWidget(self.select_file_btn)
        
        file_group.setLayout(file_layout)
        main_layout.addWidget(file_group)
        
        # 目錄顯示區域
        toc_group = QGroupBox("目錄結構")
        toc_layout = QVBoxLayout()
        
        # 使用 QScrollArea 實現可捲動的目錄列表
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        
        self.toc_widget = QWidget()
        self.toc_layout = QVBoxLayout(self.toc_widget)
        self.toc_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        scroll_area.setWidget(self.toc_widget)
        toc_layout.addWidget(scroll_area)
        
        toc_group.setLayout(toc_layout)
        main_layout.addWidget(toc_group, 1)  # 設置伸展因子為 1
        
        # 控制區域
        control_layout = QHBoxLayout()
        control_layout.setAlignment(Qt.AlignmentFlag.AlignRight)
        
        self.select_all_btn = QPushButton("全選")
        self.select_all_btn.clicked.connect(self.select_all)
        control_layout.addWidget(self.select_all_btn)
        
        self.deselect_all_btn = QPushButton("取消全選")
        self.deselect_all_btn.clicked.connect(self.deselect_all)
        control_layout.addWidget(self.deselect_all_btn)
        
        self.start_btn = QPushButton("開始分割")
        self.start_btn.clicked.connect(self.start_chunking)
        control_layout.addWidget(self.start_btn)
        
        main_layout.addLayout(control_layout)
        
        # 狀態區域
        status_layout = QHBoxLayout()
        self.status_label = QLabel("請選擇 PDF 檔案")
        status_layout.addWidget(self.status_label)
        
        main_layout.addLayout(status_layout)
        
    def select_pdf(self):
        """
        選擇 PDF 檔案並加載目錄
        """
        file_path, _ = QFileDialog.getOpenFileName(
            self, "選擇 PDF 檔案", "", "PDF 檔案 (*.pdf);;所有檔案 (*.*)"
        )
        
        if not file_path:
            return
            
        self.file_path_label.setText(file_path)
        self.status_label.setText("正在加載 PDF...")
        QApplication.processEvents()
        
        try:
            # 清空舊的目錄項目
            self.clear_toc_display()
            
            # 加載 PDF 並提取目錄
            self.chunker = PDFChunker(file_path)
            self.chunker.load_pdf()
            toc = self.chunker.extract_toc()
            
            if not toc:
                QMessageBox.warning(self, "警告", "PDF 中沒有找到目錄")
                self.status_label.setText("PDF 中沒有找到目錄")
                return
                
            # 顯示目錄
            self.display_toc(toc)
            self.status_label.setText(f"已加載 PDF: {os.path.basename(file_path)}")
            
        except Exception as e:
            QMessageBox.critical(self, "錯誤", str(e))
            self.status_label.setText(f"錯誤: {str(e)}")
            
    def clear_toc_display(self):
        """
        清除目錄顯示區域
        """
        # 清除舊的 checkboxes
        for checkbox in self.checkboxes:
            self.toc_layout.removeWidget(checkbox)
            checkbox.deleteLater()
            
        self.checkboxes = []
        self.toc_items = []
        
    def display_toc(self, toc):
        """
        顯示目錄結構
        
        Args:
            toc (list): 目錄項目列表
        """
        self.toc_items = toc
        
        # 創建目錄項目的 Checkbox
        for i, item in enumerate(toc):
            level = item["level"]
            title = item["title"]
            page = item["page"]
            
            # 根據層級設置縮進
            indent = "    " * (level - 1)
            text = f"{indent}{title} (頁面: {page})"
            
            checkbox = QCheckBox(text)
            checkbox.stateChanged.connect(lambda state, idx=i: self.handle_checkbox_change(idx, state))
            
            self.toc_layout.addWidget(checkbox)
            self.checkboxes.append(checkbox)
            
    def handle_checkbox_change(self, idx, state):
        """
        處理 Checkbox 狀態變更
        
        Args:
            idx (int): 變更的 Checkbox 索引
            state (int): Checkbox 狀態
        """
        item = self.toc_items[idx]
        level = item["level"]
        is_checked = state == Qt.CheckState.Checked.value
        item["selected"] = is_checked
        
        # 如果選中父項目，禁用所有子項目
        if is_checked:
            # 尋找所有子項目
            child_indices = []
            for i in range(idx + 1, len(self.toc_items)):
                if self.toc_items[i]["level"] <= level:
                    break
                child_indices.append(i)
                
            # 禁用子項目的 Checkbox
            for child_idx in child_indices:
                self.checkboxes[child_idx].setEnabled(False)
                self.checkboxes[child_idx].setChecked(False)
                self.toc_items[child_idx]["selected"] = False
        else:
            # 如果取消選中父項目，啟用所有子項目
            for i in range(idx + 1, len(self.toc_items)):
                if self.toc_items[i]["level"] <= level:
                    break
                self.checkboxes[i].setEnabled(True)
                
    def select_all(self):
        """
        選擇所有頂層目錄項目
        """
        for i, item in enumerate(self.toc_items):
            if item["level"] == 1:
                self.checkboxes[i].setChecked(True)
                
    def deselect_all(self):
        """
        取消選擇所有目錄項目
        """
        for i in range(len(self.toc_items)):
            self.checkboxes[i].setChecked(False)
            self.toc_items[i]["selected"] = False
            self.checkboxes[i].setEnabled(True)
            
    def start_chunking(self):
        """
        開始分割 PDF
        """
        if not self.chunker:
            QMessageBox.warning(self, "警告", "請先選擇 PDF 檔案")
            return
            
        # 檢查是否有選擇項目
        selected = [item for item in self.toc_items if item["selected"]]
        if not selected:
            QMessageBox.warning(self, "警告", "請至少選擇一個目錄項目")
            return
            
        # 詢問輸出目錄
        output_dir = QFileDialog.getExistingDirectory(self, "選擇輸出目錄")
        if not output_dir:
            return
            
        try:
            self.status_label.setText("正在分割 PDF...")
            QApplication.processEvents()
            
            # 確定分塊範圍
            chunks = self.chunker.determine_chunk_ranges(self.toc_items)
            
            # 創建分塊
            created_files = self.chunker.create_chunks(chunks, output_dir)
            
            # 顯示結果
            result_message = f"已成功創建 {len(created_files)} 個 PDF 分塊:\n\n"
            for file_path in created_files:
                result_message += f"- {os.path.basename(file_path)}\n"
                
            QMessageBox.information(self, "完成", result_message)
            self.status_label.setText(f"已完成分割: 創建了 {len(created_files)} 個 PDF 分塊")
            
        except Exception as e:
            QMessageBox.critical(self, "錯誤", str(e))
            self.status_label.setText(f"錯誤: {str(e)}")

def main():
    """
    啟動 GUI 應用程式
    """
    app = QApplication(sys.argv)
    window = PDFChunkerApp()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
