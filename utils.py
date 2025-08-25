# utils.py
import os
import fitz
import docx
import io
import logging
import difflib
from spellchecker import SpellChecker
from config import MAX_CHUNK_SIZE

logger = logging.getLogger(__name__)

def extract_text(file_path: str) -> tuple[str | None, str | None]:
    """Mengekstrak teks dari file txt, pdf, dan docx."""
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
        return None, "❌ Format file tidak didukung. Silakan kirim .txt, .pdf, atau .docx."
    except Exception as e:
        logger.error(f"Error saat ekstrak teks dari {file_path}: {e}")
        return None, f"❌ Gagal memproses file. File mungkin rusak atau terenkripsi."

def split_text_into_logical_chunks(text: str, max_chunk_size: int = MAX_CHUNK_SIZE) -> list:
    """Memecah teks menjadi beberapa bagian dengan ukuran tertentu, secara cerdas berdasarkan paragraf."""
    paragraphs = text.split('\n\n')
    chunks = []
    current_chunk = ""
    for paragraph in paragraphs:
        if len(current_chunk) + len(paragraph) + 2 <= max_chunk_size:
            current_chunk += paragraph + "\n\n"
        else:
            if current_chunk:
                chunks.append(current_chunk.strip())
            current_chunk = paragraph + "\n\n"
    if current_chunk:
        chunks.append(current_chunk.strip())
    return chunks

# Fungsi lama yang diganti
# def split_text_into_chunks(text: str, chunk_size: int) -> list:
#     """Memecah teks menjadi beberapa bagian dengan ukuran tertentu."""
#     return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def generate_diff_report(original_text: str, corrected_text: str) -> str:
    """Membuat laporan perbandingan antara teks asli dan teks yang dikoreksi."""
    if original_text.strip() == corrected_text.strip():
        return "✅ Tidak ada perubahan signifikan yang terdeteksi."

    diff = difflib.unified_diff(
        original_text.splitlines(keepends=True),
        corrected_text.splitlines(keepends=True),
        fromfile='Teks Asli', tofile='Teks Koreksi', n=2,
    )
    
    report_lines = list(diff)
    if not report_lines:
        return "✅ Tidak ada perbedaan format baris yang terdeteksi."

    report = "📝 *Laporan Perubahan Teks (Contoh):*\n\n```diff\n"
    # Batasi jumlah baris agar tidak terlalu panjang
    for line in report_lines[:25]:
        if line.startswith(('---', '+++', '@@')): continue
        report += line
    
    report += "```\n"
    if len(report_lines) > 25:
        report += "_(Laporan dipotong agar tidak terlalu panjang)_"
        
    return report

def final_spell_check(text: str) -> str:
    """Melakukan pengecekan ejaan lapisan kedua pada teks."""
    try:
        spell = SpellChecker(language='id')
        words = text.split()
        misspelled = spell.unknown(words)
        
        corrected_words = [
            word.replace(
                (clean_word := word.strip(".,!?;:()[]{}")),
                (correction if (correction := spell.correction(clean_word)) else clean_word)
            ) if clean_word.lower() in misspelled else word
            for word in words
        ]
        return " ".join(corrected_words)
    except Exception as e:
        logger.error(f"Gagal melakukan final spell check: {e}")
        return text