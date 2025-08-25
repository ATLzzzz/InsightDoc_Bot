<<<<<<< HEAD
# ai_service.py
import requests
import json
import logging
import re # Import the regular expression module
from config import GROQ_API_KEY, GROQ_MODEL, DMT_LABELS, GENERAL_LABELS

logger = logging.getLogger(__name__)

def correct_and_classify_text(text: str, is_first_chunk: bool, mode: str) -> dict:
    """Sends text to Groq API for correction and classification."""
    labels = DMT_LABELS if mode == 'DMT' else GENERAL_LABELS
    task_description = f"Klasifikasikan teks ke dalam kategori: {labels}" if is_first_chunk else "Tugas Anda hanya mengoreksi teks berikut"
    
    system_prompt = f"""
Anda adalah asisten AI untuk koreksi teks dan pembuatan data sesuai permintaan. Tugas utama Anda adalah: 
1) Memeriksa teks apakah ada kesalahan ejaan atau typo dan memperbaikinya. Jika tidak ada kesalahan, tuliskan teks aslinya sebagai nilai 'koreksi_teks'. 
2) Melaksanakan instruksi tambahan berikut: {task_description}, yang harus dijalankan setelah koreksi teks. 
Hasil akhir wajib merupakan sebuah blok kode JSON tunggal yang valid dalam format berikut: 
- Untuk bagian pertama, keluarkan {{"klasifikasi": "NAMA_KATEGORI", "koreksi_teks": "..."}} 
- Untuk bagian selanjutnya, keluarkan {{"koreksi_teks": "..."}} Berikan jawaban tanpa penjelasan atau teks tambahan, hanya blok JSON valid sesuai struktur yang ditentukan.
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
        
        try:
            # IMPROVED JSON PARSING
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_content, re.DOTALL)
            if json_match:
                json_string = json_match.group(1)
            else:
                # Fallback to the original method if no markdown block is found
                start_index = response_content.find('{')
                end_index = response_content.rfind('}')
                if start_index != -1 and end_index != -1 and end_index > start_index:
                    json_string = response_content[start_index : end_index + 1]
                else:
                    raise ValueError("Blok JSON tidak ditemukan dalam respon.")
            return json.loads(json_string)
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Gagal parsing JSON. Error: {e}. Respon mentah: {response_content}")
            return {"error": "Gagal memahami respon dari AI. Format tidak valid."}

    except requests.exceptions.RequestException as e:
        logger.error(f"Error request ke Groq API: {e}")
        return {"error": f"Gagal terhubung ke layanan AI: {e}"}
    except Exception as e:
        logger.error(f"Error tidak terduga di fungsi AI: {e}")
=======
# ai_service.py
import requests
import json
import logging
import re # Import the regular expression module
from config import GROQ_API_KEY, GROQ_MODEL, DMT_LABELS, GENERAL_LABELS

logger = logging.getLogger(__name__)

def correct_and_classify_text(text: str, is_first_chunk: bool, mode: str) -> dict:
    """Sends text to Groq API for correction and classification."""
    labels = DMT_LABELS if mode == 'DMT' else GENERAL_LABELS
    task_description = f"Klasifikasikan teks ke dalam kategori: {labels}" if is_first_chunk else "Tugas Anda hanya mengoreksi teks berikut"
    
    system_prompt = f"""
Anda adalah asisten AI untuk koreksi teks dan pembuatan data sesuai permintaan. Tugas utama Anda adalah: 
1) Memeriksa teks apakah ada kesalahan ejaan atau typo dan memperbaikinya. Jika tidak ada kesalahan, tuliskan teks aslinya sebagai nilai 'koreksi_teks'. 
2) Melaksanakan instruksi tambahan berikut: {task_description}, yang harus dijalankan setelah koreksi teks. 
Hasil akhir wajib merupakan sebuah blok kode JSON tunggal yang valid dalam format berikut: 
- Untuk bagian pertama, keluarkan {{"klasifikasi": "NAMA_KATEGORI", "koreksi_teks": "..."}} 
- Untuk bagian selanjutnya, keluarkan {{"koreksi_teks": "..."}} Berikan jawaban tanpa penjelasan atau teks tambahan, hanya blok JSON valid sesuai struktur yang ditentukan.
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
        
        try:
            # IMPROVED JSON PARSING
            json_match = re.search(r"```json\s*(\{.*?\})\s*```", response_content, re.DOTALL)
            if json_match:
                json_string = json_match.group(1)
            else:
                # Fallback to the original method if no markdown block is found
                start_index = response_content.find('{')
                end_index = response_content.rfind('}')
                if start_index != -1 and end_index != -1 and end_index > start_index:
                    json_string = response_content[start_index : end_index + 1]
                else:
                    raise ValueError("Blok JSON tidak ditemukan dalam respon.")
            return json.loads(json_string)
        except (ValueError, json.JSONDecodeError) as e:
            logger.error(f"Gagal parsing JSON. Error: {e}. Respon mentah: {response_content}")
            return {"error": "Gagal memahami respon dari AI. Format tidak valid."}

    except requests.exceptions.RequestException as e:
        logger.error(f"Error request ke Groq API: {e}")
        return {"error": f"Gagal terhubung ke layanan AI: {e}"}
    except Exception as e:
        logger.error(f"Error tidak terduga di fungsi AI: {e}")
>>>>>>> 4d3658cfa924fc51dde2eb9c6b1a60c506160a54
        return {"error": f"Terjadi kesalahan internal pada sistem AI."}