# utils.py
import os
import fitz  # PyMuPDF
import docx
import io
import logging
import difflib
from spellchecker import SpellChecker

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

def split_text_into_chunks(text: str, chunk_size: int) -> list:
    """Memecah teks menjadi beberapa bagian dengan ukuran tertentu."""
    return [text[i:i + chunk_size] for i in range(0, len(text), chunk_size)]

def generate_diff_report(original_text: str, corrected_text: str, context_lines=2) -> str:
    """Membuat laporan perbandingan antara teks asli dan teks yang dikoreksi."""
    if original_text.strip() == corrected_text.strip():
        return "✅ Tidak ada perubahan signifikan yang terdeteksi."

    diff = difflib.unified_diff(
        original_text.splitlines(keepends=True),
        corrected_text.splitlines(keepends=True),
        fromfile='Teks Asli',
        tofile='Teks Koreksi',
        n=context_lines,
    )
    
    report = "📝 *Laporan Perubahan Teks:*\n\n"
    report += "```diff\n"
    
    diff_lines = list(diff)
    if not diff_lines:
         return "✅ Tidak ada perbedaan format baris yang terdeteksi, kemungkinan hanya spasi."

    report_lines = diff_lines[:25]
    for line in report_lines:
        if line.startswith(('---', '+++', '@@')):
            continue
        report += line
    
    report += "```\n"
    if len(diff_lines) > 25:
        report += "_(Laporan dipotong agar tidak terlalu panjang)_"
        
    return report

def final_spell_check(text: str) -> str:
    """Melakukan pengecekan ejaan lapisan kedua pada teks."""
    try:
        spell = SpellChecker(language='id')
        words = text.split()
        misspelled = spell.unknown(words)
        
        corrected_words = []
        for word in words:
            clean_word = word.strip(".,!?;:()[]{}")
            if clean_word.lower() in misspelled:
                correction = spell.correction(clean_word)
                if correction:
                    corrected_words.append(word.replace(clean_word, correction))
                else:
                    corrected_words.append(word)
            else:
                corrected_words.append(word)
        return " ".join(corrected_words)
    except Exception as e:
        logger.error(f"Gagal melakukan final spell check: {e}")
        return text # Kembalikan teks asli jika terjadi error

def analyze_title(title: str) -> str:
    """Menganalisis judul penelitian dan memberikan saran perbaikan."""
    message = ""
    issues = []
    suggestions = []
    
    if len(title.split()) > 15 or len(title) > 100:
        issues.append("Judul terlalu panjang, sehingga sulit dipahami.")
        suggestions.append("Coba perpendek judul agar lebih fokus dan jelas.")

    technical_terms = ["Deep Learning", "Explainable AI", "XAI", "Grad-CAM", "Deteksi", "Visualisasi", "Manipulasi", "Deepfake"]
    found_terms = [term for term in technical_terms if term.lower() in title.lower()]
    if found_terms:
        issues.append(f"Terdapat istilah teknis yang kompleks: {', '.join(found_terms)}.")
        suggestions.append("Jika memungkinkan, jelaskan istilah ini di abstrak atau gunakan padanan yang lebih umum.")
    
    if not issues:
        return "✅ Judul sudah baik dan mudah dipahami."

    message += "📝 *Catatan Perbaikan Judul:*\n"
    for i, issue in enumerate(issues, 1):
        message += f"{i}. {issue}\n"
    message += "\n*Saran Perbaikan:*\n"
    for i, suggestion in enumerate(suggestions, 1):
        message += f"{i}. {suggestion}\n"
        
    return message