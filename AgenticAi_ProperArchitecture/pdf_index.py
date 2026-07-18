"""
Handles turning PDFs into searchable knowledge.

Two separate jobs, kept in two functions:
  - index_pdf(path):   read a PDF ONCE, chunk it, embed each chunk,
                       save to pdf_index/<filename>.json. Only needs to
                       run again if the PDF changes.
  - search_pdfs(query): search across ALL saved PDF indexes at once,
                       return the most relevant chunks regardless of
                       which PDF they came from.
"""

import os
import json
import hashlib
from pypdf import PdfReader
from sentence_transformers import SentenceTransformer
import numpy as np

PDF_INDEX_DIR = "pdf_index"

_embedding_model = SentenceTransformer("all-MiniLM-L6-v2")


def _embed(text):
    return _embedding_model.encode(text).tolist()


def _cosine_similarity(vec_a, vec_b):
    a = np.array(vec_a)
    b = np.array(vec_b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


def _chunk_text(text, chunk_size_words=200, overlap_words=40):
    """
    Splits text into overlapping chunks of ~chunk_size_words each.
    Overlap means the last ~40 words of one chunk repeat as the first
    ~40 words of the next chunk, so we don't accidentally cut a sentence
    or idea exactly in half between two chunks.
    """
    words = text.split()
    if not words:
        return []

    chunks = []
    start = 0
    while start < len(words):
        end = start + chunk_size_words
        chunk_words = words[start:end]
        chunks.append(" ".join(chunk_words))
        start = end - overlap_words  # step forward, but overlap a bit
        if end >= len(words):
            break

    return chunks


def _index_path_for(pdf_path):
    """
    Turns a PDF path into a safe index filename, e.g.
    'H:\\docs\\report.pdf' -> 'pdf_index/report_pdf_3fa91c.json'
    The short hash suffix avoids collisions between two different PDFs
    that happen to share the same filename in different folders.
    """
    os.makedirs(PDF_INDEX_DIR, exist_ok=True)
    base_name = os.path.basename(pdf_path)
    safe_name = "".join(c if c.isalnum() else "_" for c in base_name)
    path_hash = hashlib.sha1(pdf_path.encode("utf-8")).hexdigest()[:8]
    return os.path.join(PDF_INDEX_DIR, f"{safe_name}_{path_hash}.json")


def index_pdf(pdf_path):
    """
    Reads a PDF, splits it into chunks, embeds each chunk, and saves
    the result. Call this once per PDF (or again if the PDF changes).
    """
    if not os.path.isfile(pdf_path):
        return f"File not found: {pdf_path}"

    try:
        reader = PdfReader(pdf_path)
        full_text = ""
        for page in reader.pages:
            full_text += page.extract_text() or ""
    except Exception as e:
        return f"Failed to read PDF {pdf_path}: {e}"

    if not full_text.strip():
        return "No extractable text found (this may be a scanned/image-based PDF)."

    chunks = _chunk_text(full_text)

    indexed_chunks = []
    for i, chunk in enumerate(chunks):
        indexed_chunks.append({
            "chunk_index": i,
            "text": chunk,
            "embedding": _embed(chunk)
        })

    index_data = {
        "source_path": pdf_path,
        "source_filename": os.path.basename(pdf_path),
        "num_chunks": len(indexed_chunks),
        "chunks": indexed_chunks
    }

    index_path = _index_path_for(pdf_path)
    with open(index_path, "w", encoding="utf-8") as f:
        json.dump(index_data, f, indent=2)

    return f"Indexed '{os.path.basename(pdf_path)}' into {len(indexed_chunks)} chunks."


def search_pdfs(query, top_k=5, min_similarity=0.3):
    """
    Searches across every indexed PDF in pdf_index/ and returns the
    top_k most relevant chunks overall, tagged with which file each
    came from.
    """
    if not os.path.isdir(PDF_INDEX_DIR):
        return []

    query_vec = _embed(query)
    scored = []

    for filename in os.listdir(PDF_INDEX_DIR):
        if not filename.endswith(".json"):
            continue

        with open(os.path.join(PDF_INDEX_DIR, filename), "r", encoding="utf-8") as f:
            index_data = json.load(f)

        source_name = index_data.get("source_filename", "unknown.pdf")

        for chunk in index_data.get("chunks", []):
            sim = _cosine_similarity(query_vec, chunk["embedding"])
            if sim >= min_similarity:
                scored.append((sim, source_name, chunk["text"]))

    scored.sort(key=lambda item: item[0], reverse=True)
    return [
        {"source": source, "text": text}
        for _, source, text in scored[:top_k]
    ]