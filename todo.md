# PDF Chunking Tool - Todo List

## 1. Project Goal

Create a desktop application that allows users to select a PDF file, view its table of contents (ToC), and chunk the PDF into multiple smaller PDF files based on selected chapters. The application should be simple, run locally, and prioritize ease of use for PDF processing.

## 2. Technology Stack

-   **Programming Language:** Python
-   **PDF Processing Library:** `pymupdf` (or `fitz`)
-   **GUI Library:** `tkinter` (Python's built-in GUI library)

## 3. Core Features & Workflow

1.  **File Selection:**
    *   Provide a button to open a file dialog for PDF selection.
    *   (Optional) Support drag-and-drop of PDF files onto the application window.
2.  **PDF Loading & ToC Extraction:**
    *   Load the selected PDF using `pymupdf`.
    *   Extract the Table of Contents (ToC) from the PDF. Each ToC entry should include title, level, and starting page number.
3.  **Display ToC & User Selection:**
    *   Display the extracted ToC in a hierarchical (tree-like or indented) list.
    *   Each ToC entry should have a checkbox for selection.
    *   **Selection Logic:**
        *   If a parent chapter is checked, all its child chapters are implicitly included in that chunk. The checkboxes for child chapters should appear disabled (greyed out) to reflect this.
        *   If a parent chapter is *not* checked, its child chapters can be individually checked. Each individually checked child chapter will form a separate chunk.
4.  **Chunking Process:**
    *   Based on user selections, determine the page ranges for each chunk.
    *   For each determined chunk, create a new PDF file containing the specified pages from the original PDF.
5.  **Output:**
    *   Save the generated chunked PDF files to the same directory as the original PDF file.
    *   **File Naming Convention:** `[OriginalFileName]_[SelectedChapterTitle].pdf`. Ensure chapter titles are sanitized for valid filenames (remove/replace characters like `/`, `\`, `:`, `*`, `?`, `"`, `<`, `>`, `|`).

## 4. UI Details (tkinter)

-   **Main Window:** Application's main container.
-   **File Selection Area:**
    *   "Select PDF" button.
    *   Label to display the path of the selected PDF.
-   **Chapter List Area:**
    *   Use `tkinter.ttk.Treeview` or a scrollable frame with `Checkbutton` widgets to display the ToC.
    *   Implement logic to disable/enable child checkboxes based on parent checkbox state.
-   **Controls:**
    *   "Start Chunking" button.
-   **Status/Feedback Area:**
    *   A label or text area to display messages (e.g., "Processing...", "Chunking complete", error messages).

## 5. PDF Processing Logic (pymupdf)

-   **Load PDF:** Function to open and validate a PDF file.
-   **Extract ToC:**
    *   Use `doc.get_toc(simple=False)` to get detailed ToC information (level, title, page).
    *   Store ToC data in a structured way (e.g., list of dictionaries or custom objects) to facilitate GUI display and processing.
-   **Determine Chunk Ranges:**
    *   Iterate through the selected ToC items in the GUI.
    *   If a parent chapter is selected:
        *   Start Page: Parent chapter's start page.
        *   End Page: Page before the start of the *next* ToC entry that is at the same or a higher level than the current parent chapter. If it's the last major section, then up to the end of the PDF.
    *   If an individual child chapter (whose parent is not selected) is selected:
        *   Start Page: Child chapter's start page.
        *   End Page: Page before the start of the *next* ToC entry (regardless of level). If it's the last ToC entry, then up to the end of the PDF.
-   **Create Chunks:**
    *   For each chunk range (start_page, end_page):
        *   Create a new `fitz.Document()`.
        *   Use `new_doc.insert_pdf(original_doc, from_page=start_page-1, to_page=end_page-1)` (pymupdf pages are 0-indexed, ToC pages are usually 1-indexed).
        *   Save the `new_doc` with the specified naming convention.

## 6. Error Handling and Edge Cases

-   **No ToC:** If `doc.get_toc()` returns an empty list or `None`, display a message: "No Table of Contents found in this PDF."
-   **Encrypted/Unreadable PDF:** If `pymupdf` fails to open the PDF (e.g., due to encryption without password or corruption), display: "Cannot read PDF. File might be encrypted or corrupted."
-   **Invalid File Selection:** Handle cases where a non-PDF file is selected.
-   **File I/O Errors:** Handle potential errors during saving of chunked files (e.g., disk full, permissions).
-   **Filename Sanitization:** Implement a robust function to clean chapter titles for use in filenames.

## 7. Implementation Steps (High-Level)

1.  **Setup Project:** Create project directory, virtual environment (optional but recommended).
2.  **Basic UI Layout:** Design the main window with `tkinter` (file selection, ToC area, button, status label).
3.  **PDF Loading & ToC Display:**
    *   Implement PDF file selection logic.
    *   Implement `pymupdf` logic to load PDF and extract ToC.
    *   Populate the ToC display area in the GUI, including checkboxes and hierarchy.
    *   Implement checkbox interaction logic (parent selection disabling children).
4.  **Chunking Logic:**
    *   Implement the algorithm to determine chunk page ranges based on selections.
    *   Implement `pymupdf` logic to create and save new PDF chunks.
5.  **Integration & Testing:**
    *   Connect the "Start Chunking" button to the chunking logic.
    *   Thoroughly test with various PDFs (different ToC structures, sizes).
6.  **Error Handling & Refinements:**
    *   Implement all defined error handling.
    *   Refine UI and user experience.

## 8. Future Considerations (Optional)

-   Progress bar for chunking large PDFs.
-   Option for user to select a custom output directory.
-   Preview of chapter page ranges before chunking.
-   Support for editing ToC entries if PDF metadata is incorrect (advanced).
