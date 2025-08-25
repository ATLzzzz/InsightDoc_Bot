def analyze_title(title: str) -> str:
    """Analyzes a research title and returns a correction message with suggestions in simple language."""
    message = ""
    issues = []
    suggestions = []

    # Check for length/complexity
    if len(title.split()) > 12 or len(title) > 90:
        issues.append("Judul terlalu panjang atau kompleks, sehingga sulit dipahami.")
        suggestions.append("Cobalah memecah judul menjadi frasa yang lebih pendek dan jelas.")

    # Check for technical jargon
    technical_terms = ["Deep Learning", "Explainable AI", "XAI", "Grad-CAM", "Deteksi", "Visualisasi", "Manipulasi", "Deepfake"]
    found_terms = [term for term in technical_terms if term.lower() in title.lower()]
    if found_terms:
        issues.append(f"Terdapat istilah teknis: {', '.join(found_terms)} yang mungkin membingungkan pembaca awam.")
        suggestions.append("Jelaskan istilah teknis tersebut secara singkat di judul atau deskripsi.")

    # Check for ambiguity (method, application, context all mixed)
    if ("Grad-CAM" in title or "Explainable AI" in title or "XAI" in title) and ("Deepfake" in title) and ("Kampanye Politik" in title or "Politik" in title):
        issues.append("Fokus judul kurang jelas, apakah pada metode, aplikasi, atau konteks.")
        suggestions.append("Tentukan fokus utama: metode, aplikasi, atau konteks, lalu susun ulang judul agar lebih terarah.")

    # Compose message
    if not issues:
        return "Judul sudah cukup baik dan mudah dipahami."

    message += "\n\u2B06\uFE0F *Catatan Perbaikan Judul:*\n"
    for i, issue in enumerate(issues, 1):
        message += f"{i}. {issue}\n"
    message += "\n*Usulan Perbaikan:*\n"
    for i, suggestion in enumerate(suggestions, 1):
        message += f"{i}. {suggestion}\n"
    message += ("\nContoh judul yang lebih sederhana:\n"
                "'Penerapan Deep Learning dan Explainable AI untuk Deteksi Deepfake pada Video Politik'\n"
                "Atau tambahkan penjelasan singkat istilah di deskripsi.")
    return message
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