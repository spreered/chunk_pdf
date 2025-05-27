# PDF Chunking Tool

A desktop application that allows users to select a PDF file, view its table of contents, and chunk the PDF into multiple smaller PDF files based on selected chapters. The application runs locally and prioritizes ease of use for PDF processing.

## Features

- **File Selection**: Provides a button to open a file dialog for PDF selection
- **ToC Extraction**: Automatically extracts the Table of Contents (ToC) from the PDF
- **Hierarchical Display**: Shows the PDF ToC in a tree-like structure for easy selection
- **Smart Selection**:
  - When a parent chapter is selected, all its child chapters are automatically included in the same chunk
  - When a parent chapter is not selected, child chapters can be individually selected
- **Automatic Chunking**: Automatically determines page ranges and creates new PDF files based on selected chapters
- **Friendly Naming**: Chunked files are named using the original filename plus the chapter title

## Technology Stack

- **Programming Language**: Python
- **PDF Processing**: PyMuPDF (fitz)
- **GUI Framework**: PySide6 (Qt for Python)

## Installation

### Requirements

- Python 3.8 or higher
- Supported Operating Systems: Windows, macOS, Linux

### Setup

1. Clone or download this project to your local machine

2. Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

1. Launch the application:

```bash
python pdf_chunker_gui.py
```

2. Click the "Select PDF" button to choose a PDF file to process

3. Check the chapters you want to split in the ToC list:
   - Checking a parent chapter will automatically include all its child chapters
   - When a parent chapter is not checked, child chapters can be individually checked

4. Click the "Start Chunking" button

5. Select an output directory

6. Wait for the process to complete; the system will display a list of created PDF chunk files

## Creating a Standalone Application (macOS)

You can create a standalone macOS application (`.app` bundle) using PyInstaller. This allows users to run the application without needing to install Python or any dependencies.

1.  **Install PyInstaller**:
    If you haven't already, install PyInstaller:
    ```bash
    pip install pyinstaller
    ```

2.  **Navigate to the project directory**:
    Open your terminal and change to the project's root directory:
    ```bash
    cd path/to/your/chunk_pdf
    ```

3.  **Run PyInstaller**:
    Use the following command to build the application. This command creates a single executable file within an `.app` bundle, suitable for GUI applications.
    ```bash
    pyinstaller --name "PDFChunker" --onefile --windowed --icon="path/to/your/icon.icns" pdf_chunker_gui.py
    ```
    *   `--name "PDFChunker"`: Sets the name of your application.
    *   `--onefile`: Bundles everything into a single executable inside the `.app`.
    *   `--windowed`: Prevents a terminal console window from appearing when the GUI app runs.
    *   `--icon="path/to/your/icon.icns"`: (Optional) Specifies the path to your custom application icon (`.icns` file). If you don't have one, you can omit this or create one.
    *   `pdf_chunker_gui.py`: The main script for your application.

4.  **Find the application**:
    After PyInstaller finishes, you will find the `PDFChunker.app` (or the name you specified) inside the `dist` directory within your project folder.

5.  **Distribute**:
    You can then distribute this `.app` file. For wider distribution, consider code signing and notarization for macOS. The generated `.app` file should **not** be committed to the Git repository; instead, use GitHub Releases to distribute it.

**Note on `.gitignore`**:
Ensure that PyInstaller's build artifacts are ignored by Git. The `.gitignore` file in this project should already include:
```gitignore
build/
dist/
*.spec
```

## File Description

- `pdf_chunker.py`: Core logic class for handling PDF loading, ToC extraction, and chunking functionality
- `pdf_chunker_gui.py`: GUI implementation using PySide6 to create the user interface
- `test_chunker.py`: Test script for testing core logic functionality
- `create_test_pdf.py`: Script for creating test PDF files
- `requirements.txt`: List of dependencies

## Error Handling

The application handles the following situations:

- **No ToC**: If the PDF has no table of contents, a warning message is displayed
- **Encrypted/Unreadable PDF**: If the PDF cannot be opened, an error message is displayed
- **File I/O Errors**: Handles potential errors when saving chunked files
- **Filename Sanitization**: Automatically cleans invalid characters in chapter titles to ensure valid filenames

## License

This project is licensed under the MIT License.

## Contributing

Feel free to submit issue reports, feature requests, or contribute code directly.
