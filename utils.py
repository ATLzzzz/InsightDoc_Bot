# utils.py
import os
import fitz  # PyMuPDF
import docx
import io
import logging

logger = logging.getLogger(__name__)

def extract_text(file_path: str):
    """Extracts text from txt, pdf, and docx files."""
    ext = os.path.splitext(file_path)[-1].lower()
    try:
        with open(file_path, "rb") as f:
            content = f.read()
        if ext == ".txt":
            return content.decode("utf-8", errors='ignore'), None
        if ext == ".pdf":
            with fitz.open(stream=content, filetype="pdf") as doc:
                return "\n".join(page.get_text() for page in doc), None
        if ext == ".docx":
            doc = docx.Document(io.BytesIO(content))
            return "\n".join(p.text for p in doc.paragraphs), None
        return None, "❌ Format file tidak didukung."
    except Exception as e:
        logger.error(f"Error ekstrak teks: {e}")
        return None, f"❌ Gagal memproses file."

def split_text_into_chunks(text: str, chunk_size: int) -> list:
    """Splits a string into chunks of a specified size."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]