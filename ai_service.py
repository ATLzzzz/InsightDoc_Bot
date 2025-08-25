# ai_service.py
import requests
import json
import logging
import re
from config import GROQ_API_KEY, GROQ_MODEL, DMT_LABELS, GENERAL_LABELS

logger = logging.getLogger(__name__)

def correct_and_classify_text(text: str, is_first_chunk: bool, mode: str) -> dict:
    """Mengirim teks ke Groq API untuk koreksi dan klasifikasi dengan instruksi super detail."""
    labels = DMT_LABELS if mode == 'DMT' else GENERAL_LABELS
    
    # Prompt telah disederhanakan agar lebih jelas dan langsung ke inti
    system_prompt = f"""
Anda adalah asisten yang cerdas dan teliti. Tugas Anda adalah menyunting teks yang diberikan dengan standar PUEBI dan KBBI, serta mengklasifikasikannya jika itu adalah bagian pertama dari dokumen.

**Instruksi:**
1.  **Sunting Teks:** Perbaiki semua kesalahan ejaan, tata bahasa, dan tanda baca.
2.  **Klasifikasi (Hanya Bagian Pertama):**
    -   Jika ini adalah bagian pertama dokumen, klasifikasikan isinya ke dalam salah satu kategori ini: {', '.join(labels)}.
    -   Jika bukan bagian pertama, abaikan klasifikasi dan hanya lakukan penyuntingan.

**Format Output (WAJIB JSON):**
-   **Untuk bagian pertama:** `{{"klasifikasi": "NAMA_KATEGORI", "koreksi_teks": "..."}}`
-   **Untuk bagian selanjutnya:** `{{"koreksi_teks": "..."}}`

Hanya outputkan satu blok kode JSON yang valid tanpa teks tambahan di luar blok tersebut.
"""
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": text}],
                "temperature": 0.1, "top_p": 0.9,
            },
            timeout=180
        )
        response.raise_for_status()
        response_content = response.json()["choices"][0]["message"]["content"]
        
        try:
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_content, re.DOTALL)
            json_string = json_match.group(1) if json_match else response_content[response_content.find('{') : response_content.rfind('}') + 1]
            if not json_string: raise ValueError("Blok JSON tidak ditemukan.")
            
            # Cek jika klasifikasi ada dan tidak kosong, jika tidak, berikan default
            data = json.loads(json_string)
            if 'klasifikasi' in data and not data['klasifikasi']:
                data['klasifikasi'] = "Tidak Diketahui"
            
            return data
        except (ValueError, json.JSONDecodeError, AttributeError) as e:
            logger.error(f"Gagal parsing JSON: {e}. Respon mentah: {response_content}")
            return {"error": "Gagal memahami respons dari AI."}
    except requests.exceptions.RequestException as e:
        logger.error(f"Error request ke Groq API: {e}")
        return {"error": f"Gagal terhubung ke layanan AI: {e}"}
    except Exception as e:
        logger.error(f"Error tidak terduga di fungsi AI: {e}")
        return {"error": f"Terjadi kesalahan internal pada sistem AI."}

def analyze_title_for_dmt(title: str) -> str:
    """Menganalisis judul penelitian secara spesifik untuk mode DMT (Dewan Musyawarah Taruna)."""
    dmt_commissions = ["KOMISI I", "KOMISI II", "KOMISI III", "KOMISI IV"]

    system_prompt = f"""
Anda adalah seorang **Dosen Pembimbing Akademik dan Panitia Dewan Musyawarah Taruna (DMT)** yang sangat berpengalaman. Tugas Anda adalah memberikan analisis tajam dan konstruktif terhadap judul penelitian berikut, dengan fokus khusus pada relevansinya dengan **empat komisi utama DMT**.

**Judul yang akan dianalisis:** "{title}"

**Analisis Anda harus mencakup poin-poin berikut:**
1.  **Relevansi dengan Komisi DMT**: Kelompokkan dan diskusikan relevansi judul ini secara terperinci dengan salah satu dari empat komisi berikut: {', '.join(dmt_commissions)}. Jika judul relevan dengan lebih dari satu komisi, jelaskan setiap relevansinya. Jika tidak relevan, nyatakan demikian.
2.  **Fokus Penelitian dan Jangkauan**: Apakah fokus utama (metode, objek, atau tujuan) sudah tergambar dengan jelas? Apakah cakupannya terlalu luas atau terlalu sempit untuk konteks DMT?
3.  **Saran Perbaikan Berbasis Komisi**: Berikan 1-2 alternatif atau contoh judul yang lebih baik, spesifik, dan lebih terarah pada salah satu komisi yang relevan.

**Format Output:**
Berikan jawaban dalam format Markdown yang rapi. Gunakan poin-poin dan buatlah agar mudah dibaca. Berikan langsung sebagai teks biasa tanpa format JSON.
"""
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "system", "content": system_prompt}],
                "temperature": 0.3,
            },
            timeout=120
        )
        response.raise_for_status()
        feedback = response.json()["choices"][0]["message"]["content"]
        return feedback
    except requests.exceptions.RequestException as e:
        logger.error(f"Error request ke Groq API saat analisis judul: {e}")
        return f"❌ Gagal terhubung ke layanan AI: {e}"
    except Exception as e:
        logger.error(f"Error tidak terduga di fungsi analisis judul: {e}")
        return f"❌ Terjadi kesalahan internal pada sistem AI."

def analyze_title_with_llm(title: str) -> str:
    """Menganalisis judul penelitian menggunakan LLM untuk memberikan feedback mendalam."""
    system_prompt = f"""
Anda adalah seorang **Dosen Pembimbing Akademik dan Reviewer Jurnal Ilmiah** yang sangat berpengalaman. Tugas Anda adalah memberikan analisis tajam dan konstruktif terhadap judul penelitian berikut.

**Judul yang akan dianalisis:** "{title}"

**Analisis Anda harus mencakup poin-poin berikut:**
1.  **Kejelasan dan Kepadatan**: Apakah judulnya terlalu panjang, berbelit-belit, atau mudah dipahami? Berikan komentar.
2.  **Penggunaan Istilah Teknis (Jargon)**: Apakah ada istilah teknis yang kompleks? Sarankan apakah perlu disederhanakan atau dijelaskan.
3.  **Fokus Penelitian**: Apakah fokus utama (metode, objek, atau tujuan) sudah tergambar dengan jelas?
4.  **Saran Perbaikan**: Berikan 1-2 alternatif atau contoh judul yang lebih baik, lebih singkat, atau lebih menarik.

**Format Output:**
Berikan jawaban dalam format Markdown yang rapi. Gunakan poin-poin dan buatlah agar mudah dibaca. Jangan memberikan jawaban dalam format JSON. Berikan langsung sebagai teks biasa.
"""
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "system", "content": system_prompt}],
                "temperature": 0.3,
            },
            timeout=120
        )
        response.raise_for_status()
        feedback = response.json()["choices"][0]["message"]["content"]
        return feedback
    except requests.exceptions.RequestException as e:
        logger.error(f"Error request ke Groq API saat analisis judul: {e}")
        return f"❌ Gagal terhubung ke layanan AI: {e}"
    except Exception as e:
        logger.error(f"Error tidak terduga di fungsi analisis judul: {e}")
        return f"❌ Terjadi kesalahan internal pada sistem AI."