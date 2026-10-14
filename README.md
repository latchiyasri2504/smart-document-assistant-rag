# Smart Document Assistant

A beginner-friendly document question assistant demonstrating document ingestion, parsing, structure-aware chunking, and retrieval.

## Features
- Upload PDF, DOCX, or TXT files
- Extract document text locally in the app process
- Split text into sentence-aware chunks with modest overlap
- Find relevant passages using TF-IDF similarity
- Show source section/page information when available

## Requirements
- Python 3.10 or newer
- Visual Studio Code (recommended)

## Run on Windows
1. Open this folder in VS Code.
2. Open Terminal → New Terminal.
3. Create a virtual environment:
   `python -m venv venv`
4. Activate it in PowerShell:
   `.env\Scripts\Activate.ps1`
   If PowerShell blocks activation, use Command Prompt terminal and run:
   `venv\Scripts\activate.bat`
5. Install dependencies:
   `python -m pip install -r requirements.txt`
6. Start the app:
   `python -m streamlit run app.py`
7. Open the local URL shown in the terminal, usually `http://localhost:8501`.

## Test
Upload a text-based PDF or DOCX. Ask a question whose answer appears in the document. Check the returned passages and page/section metadata.

## Important limitations
- This starter version retrieves relevant passages; it does not call an LLM to compose a fluent generated answer.
- Scanned/image-only PDFs need OCR, not included here.
- The current chunker is a simple rule-based demonstration. For production use, validate table extraction, OCR, token limits, access controls, and retrieval metrics.
- Do not upload confidential documents to a public deployment without appropriate security and consent.
