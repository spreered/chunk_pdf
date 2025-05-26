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
