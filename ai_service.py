# ai_service.py
import requests
import json
import logging
import re
from config import GROQ_API_KEY, GROQ_MODEL, DMT_LABELS, GENERAL_LABELS

logger = logging.getLogger(__name__)

def correct_and_classify_text(text: str, is_first_chunk: bool, mode: str) -> dict:
    """Mengirim teks ke Groq API untuk koreksi dan klasifikasi dengan instruksi yang lebih detail."""
    labels = DMT_LABELS if mode == 'DMT' else GENERAL_LABELS
    
    # ---- INSTRUKSI BARU YANG LEBIH CERDAS ----
    system_prompt = f"""
Anda adalah seorang editor ahli Bahasa Indonesia yang bertugas untuk menyempurnakan teks.
Tugas Anda adalah sebagai berikut:
1.  **Koreksi Ejaan dan Tanda Baca**: Perbaiki semua kesalahan pengetikan (typo), ejaan, dan penggunaan tanda baca sesuai standar PUEBI dan KBBI.
2.  **Perbaiki Gaya Bahasa**: Ubah kalimat yang kaku, ambigu, atau tidak efektif menjadi kalimat yang lebih jelas, profesional, dan mudah dipahami.
3.  **Tingkatkan Pilihan Kata (Diksi)**: Ganti kata-kata yang kurang formal atau kurang tepat dengan sinonim yang lebih sesuai untuk konteks akademis atau teknis.
4.  **Klasifikasi (Hanya untuk Bagian Pertama)**: {'Jika ini adalah bagian pertama teks, klasifikasikan isinya ke dalam salah satu kategori berikut: ' + ', '.join(labels) + '.' if is_first_chunk else 'Anda tidak perlu melakukan klasifikasi untuk bagian ini.'}

Hasil akhir WAJIB berupa satu blok kode JSON yang valid tanpa teks tambahan di luar blok tersebut.
-   Untuk bagian pertama: `{{"klasifikasi": "NAMA_KATEGORI", "koreksi_teks": "..."}}`
-   Untuk bagian selanjutnya: `{{"koreksi_teks": "..."}}`

Pastikan `koreksi_teks` berisi versi teks yang sudah disempurnakan sepenuhnya.
"""
    # ---------------------------------------------
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": text}],
                "temperature": 0.1, # Sedikit kreativitas untuk perbaikan gaya bahasa
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