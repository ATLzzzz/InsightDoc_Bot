# config.py
import os
from dotenv import load_dotenv

# Muat variabel dari file .env
load_dotenv()

# --- TOKENS & KEYS ---
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
GROQ_API_KEY = os.getenv('GROQ_API_KEY')

if not TELEGRAM_TOKEN or not GROQ_API_KEY:
    raise EnvironmentError("PENTING: Harap atur TELEGRAM_TOKEN dan GROQ_API_KEY dalam file .env atau sebagai environment variable.")

# --- BOT & AI SETTINGS ---
GROQ_MODEL = "llama3-8b-8192"
try:
    ADMIN_ID = int(os.getenv('ADMIN_ID'))
except (TypeError, ValueError):
    raise EnvironmentError("PENTING: Harap atur ADMIN_ID dalam file .env dengan nilai integer yang valid.")

MAX_CHUNK_SIZE = 12000 # Ukuran chunk untuk dianalisis oleh AI

# --- DATA & LABELS ---
USER_DATA_FILE = "user_data.json"
DMT_LABELS = ["KOMISI I", "KOMISI II", "KOMISI III", "KOMISI IV", "Badan Pengurus Harian"]
GENERAL_LABELS = ["Surat Resmi", "Laporan", "Artikel", "Pendidikan", "Catatan Pribadi", "Lainnya"]