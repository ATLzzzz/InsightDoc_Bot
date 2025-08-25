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
    
    # ---- INSTRUKSI BARU YANG SANGAT TEGAS DAN DETAIL ----
    system_prompt = f"""
Anda adalah seorang **Redaktur Ahli dari Balai Pustaka** yang memiliki standar kesempurnaan tertinggi. Tugas Anda adalah memeriksa dan menyunting teks berikut dengan sangat teliti.

**DAFTAR PERIKSA WAJIB ANDA:**
1.  **Ejaan dan Typo (Tanpa Toleransi)**: Perbaiki SEMUA kesalahan pengetikan, sekecil apa pun. Gunakan **PUEBI dan KBBI** sebagai acuan mutlak.
2.  **Tanda Baca**: Pastikan semua koma, titik, spasi, tanda hubung, dan tanda baca lainnya digunakan dengan benar. Perbaiki spasi ganda atau spasi yang tidak perlu (misalnya: "kata : kata" menjadi "kata: kata").
3.  **Tata Bahasa dan Struktur Kalimat**: Susun ulang kalimat yang ambigu atau tidak efektif agar menjadi jelas, logis, dan profesional.
4.  **Konsistensi Istilah**: Pastikan istilah teknis dan nama (contoh: "website" vs "aplikasi web") digunakan secara konsisten di seluruh teks.
5.  **Kesalahan Kontekstual**: Identifikasi kesalahan yang hanya bisa dipahami dari konteks, seperti tahun yang tidak lengkap (contoh: `202` harus menjadi `2024` jika konteksnya adalah laporan saat ini).
6.  **Klasifikasi (Hanya Jika Diperintahkan)**: {'Jika ini adalah bagian pertama teks, klasifikasikan isinya ke dalam salah satu kategori berikut: ' + ', '.join(labels) + '.' if is_first_chunk else 'Fokus Anda 100% pada penyuntingan, abaikan klasifikasi.'}

**FORMAT OUTPUT (WAJIB):**
Keluarkan HANYA satu blok kode JSON yang valid. Jangan tambahkan komentar atau penjelasan apa pun di luar JSON.
-   Untuk bagian pertama: `{{"klasifikasi": "NAMA_KATEGORI", "koreksi_teks": "..."}}`
-   Untuk bagian selanjutnya: `{{"koreksi_teks": "..."}}`

Teks di dalam "koreksi_teks" harus menjadi versi final yang sudah sempurna tanpa ada satu pun kesalahan yang tersisa.
"""
    # ----------------------------------------------------
    
    try:
        # (Sisa kode di file ini tetap sama, tidak perlu diubah)
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": text}],
                "temperature": 0.1,
                "top_p": 0.9,
            },
            timeout=180
        )
        response.raise_for_status()
        response_content = response.json()["choices"][0]["message"]["content"]
        
        try:
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_content, re.DOTALL)
            if json_match:
                json_string = json_match.group(1)
            else:
                start_index = response_content.find('{')
                end_index = response_content.rfind('}')
                if start_index != -1 and end_index > start_index:
                    json_string = response_content[start_index : end_index + 1]
                else:
                    logger.error(f"Blok JSON tidak ditemukan dalam respons AI: {response_content}")
                    return {"error": "AI tidak memberikan respons dalam format JSON yang valid."}
            
            return json.loads(json_string)

        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Gagal parsing JSON. Error: {e}. Respon mentah: {response_content}")
            return {"error": "Gagal memahami respons dari AI. Format tidak valid."}

    except requests.exceptions.RequestException as e:
        logger.error(f"Error request ke Groq API: {e}")
        return {"error": f"Gagal terhubung ke layanan AI: {e}"}
    except Exception as e:
        logger.error(f"Error tidak terduga di fungsi AI: {e}")
        return {"error": f"Terjadi kesalahan internal pada sistem AI."}