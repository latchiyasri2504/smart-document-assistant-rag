import re
from pathlib import Path

import streamlit as st
from pypdf import PdfReader
from docx import Document
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

st.set_page_config(page_title="Smart Document Assistant", page_icon="📄", layout="wide")
st.title("📄 Smart Document Assistant")
st.write("Upload a PDF, DOCX, or TXT file and ask questions based on its content.")
st.caption("This starter project processes uploaded files in the app session. Answers are based on matching document passages, not a hosted LLM.")

def extract_text(uploaded_file):
    name = uploaded_file.name.lower()
    if name.endswith(".pdf"):
        reader = PdfReader(uploaded_file)
        pages = []
        for i, page in enumerate(reader.pages, start=1):
            text = page.extract_text() or ""
            if text.strip():
                pages.append({"text": text, "page": i, "section": f"Page {i}"})
        return pages
    if name.endswith(".docx"):
        doc = Document(uploaded_file)
        blocks, current_heading = [], "Document"
        for paragraph in doc.paragraphs:
            text = paragraph.text.strip()
            if not text:
                continue
            if paragraph.style and paragraph.style.name.startswith("Heading"):
                current_heading = text
            blocks.append({"text": text, "page": None, "section": current_heading})
        return blocks
    if name.endswith(".txt"):
        raw = uploaded_file.getvalue().decode("utf-8", errors="replace")
        return [{"text": raw, "page": None, "section": "Text file"}]
    raise ValueError("Unsupported file type. Please upload PDF, DOCX, or TXT.")

def split_into_chunks(blocks, max_words=180, overlap=30):
    """Structure-aware starter chunker: split paragraphs by sentence when too long."""
    chunks = []
    for block in blocks:
        text = re.sub(r"\s+", " ", block["text"]).strip()
        if not text:
            continue
        sentences = re.split(r"(?<=[.!?])\s+", text)
        current = []
        count = 0
        for sentence in sentences:
            words = sentence.split()
            if not words:
                continue
            if count + len(words) > max_words and current:
                chunks.append({
                    "text": " ".join(current),
                    "page": block.get("page"),
                    "section": block.get("section", "Document")
                })
                carry = " ".join(current).split()[-overlap:] if overlap else []
                current = carry + words
                count = len(current)
            else:
                current.extend(words)
                count += len(words)
        if current:
            chunks.append({
                "text": " ".join(current),
                "page": block.get("page"),
                "section": block.get("section", "Document")
            })
    return chunks

def find_relevant_chunks(question, chunks, top_k=3):
    texts = [c["text"] for c in chunks]
    if not texts or not question.strip():
        return []
    vectorizer = TfidfVectorizer(stop_words="english")
    try:
        matrix = vectorizer.fit_transform(texts + [question])
    except ValueError:
        return []
    scores = cosine_similarity(matrix[-1], matrix[:-1]).flatten()
    ranked = scores.argsort()[::-1][:top_k]
    return [dict(chunks[i], score=float(scores[i])) for i in ranked if scores[i] > 0]

uploaded = st.file_uploader("Choose a document", type=["pdf", "docx", "txt"])
if uploaded:
    try:
        blocks = extract_text(uploaded)
        chunks = split_into_chunks(blocks)
        st.success(f"Document processed: {len(blocks)} content blocks and {len(chunks)} chunks.")
        with st.expander("Preview extracted text"):
            preview = "\n\n".join(b["text"] for b in blocks)
            st.text(preview[:8000] or "No selectable text found. Scanned PDFs need OCR, which this starter version does not include.")
        question = st.text_input("Ask a question about your document", placeholder="Example: What is dynamic chunking?")
        if st.button("Find answer", type="primary", disabled=not question.strip()):
            matches = find_relevant_chunks(question, chunks)
            if not matches:
                st.warning("No matching passage was found. Try different keywords or check whether the document contains selectable text.")
            else:
                st.subheader("Relevant answer passages")
                st.write("The passages below are the closest matches found in your document. Read them as evidence; this basic version does not generate new facts.")
                for i, item in enumerate(matches, start=1):
                    location = item["section"]
                    if item.get("page"):
                        location += f" • Page {item['page']}"
                    st.markdown(f"**Source {i}: {location}**")
                    st.write(item["text"])
                    st.caption(f"Keyword relevance score: {item['score']:.3f}")
    except Exception as exc:
        st.error(f"Could not process this file: {exc}")
else:
    st.info("Start by uploading a document. Try your project PDF or the RAG Dynamic Parsing and Chunking PDF.")
