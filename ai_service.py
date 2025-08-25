# ai_service.py
import requests
import json
import logging
import re
from config import GROQ_API_KEY, GROQ_MODEL, DMT_LABELS, GENERAL_LABELS

logger = logging.getLogger(__name__)

def correct_and_classify_text(text: str, is_first_chunk: bool, mode: str) -> dict:
    """Mengirim teks ke Groq API untuk koreksi dan klasifikasi."""
    labels = DMT_LABELS if mode == 'DMT' else GENERAL_LABELS
    task_description = f"Klasifikasikan teks ke dalam salah satu kategori berikut: {', '.join(labels)}."
    
    # Instruksi yang lebih jelas untuk AI
    system_prompt = f"""
Anda adalah asisten AI yang bertugas mengoreksi dan mengklasifikasi teks.
Tugas Anda:
1.  **Koreksi Teks**: Perbaiki semua kesalahan ejaan dan typo dalam teks yang diberikan. Jika tidak ada kesalahan, kembalikan teks aslinya.
2.  **Instruksi Tambahan**: {'Lakukan klasifikasi berdasarkan deskripsi ini: ' + task_description if is_first_chunk else 'Anda hanya perlu melakukan koreksi teks.'}

Format output WAJIB berupa satu blok kode JSON yang valid.
-   Untuk bagian pertama (is_first_chunk=True): `{{"klasifikasi": "NAMA_KATEGORI", "koreksi_teks": "..."}}`
-   Untuk bagian selanjutnya: `{{"koreksi_teks": "..."}}`

Jangan tambahkan penjelasan atau teks lain di luar blok JSON.
"""
    
    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {GROQ_API_KEY}", "Content-Type": "application/json"},
            json={
                "model": GROQ_MODEL,
                "messages": [{"role": "system", "content": system_prompt}, {"role": "user", "content": text}],
                "temperature": 0.0,
            },
            timeout=180
        )
        response.raise_for_status()
        response_content = response.json()["choices"][0]["message"]["content"]
        
        # Logika parsing JSON yang lebih andal
        try:
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_content, re.DOTALL)
            if json_match:
                json_string = json_match.group(1)
            else:
                # Fallback jika tidak ada blok markdown ```json
                start_index = response_content.find('{')
                end_index = response_content.rfind('}')
                if start_index != -1 and end_index > start_index:
                    json_string = response_content[start_index : end_index + 1]
                else:
                    # Jika tidak ditemukan JSON sama sekali
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