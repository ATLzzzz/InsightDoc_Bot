# InsightDoc 🤖📄

![InsightDoc Logo](logo.png)

*Asisten cerdas Anda untuk analisis, koreksi, dan klasifikasi dokumen di Telegram.*

---

InsightDoc adalah bot Telegram canggih yang dibangun dengan Python dan memanfaatkan kekuatan Groq LPU™ Inference Engine serta Llama 3 untuk menganalisis dokumen yang dikirimkan pengguna. Bot ini dapat mengekstrak teks dari berbagai format berkas, mengoreksi ejaan dan salah ketik, serta mengklasifikasikan konten dokumen ke dalam kategori yang telah ditentukan.

Bot ini dirancang untuk menjadi alat yang cepat dan efisien untuk menyortir dan membersihkan dokumen secara langsung di dalam obrolan Telegram Anda.

---

## Fitur

-   **📄 Dukungan Dokumen Multi-Format**: Memproses berkas `.txt`, `.pdf`, dan `.docx` dengan lancar.
-   **🧠 Koreksi Berbasis AI**: Secara otomatis mengidentifikasi dan memperbaiki kesalahan ejaan dan salah ketik dalam teks dokumen.
-   **🏷️ Klasifikasi Dua Mode**:
    -   **Mode DMT**: Mengklasifikasikan dokumen ke dalam kategori organisasi tertentu (`KOMISI I`, `KOMISI II`, dll.).
    -   **Mode Umum**: Mengklasifikasikan dokumen ke dalam kategori yang lebih luas (`Surat Resmi`, `Laporan`, dll.).
-   **👤 Pelacakan Pengguna & Penggunaan**: Mencatat interaksi pengguna, melacak jumlah penggunaan dan waktu aktivitas dalam berkas `user_data.json`.
-   **🔐 Akses Khusus Admin**: Menyertakan perintah `/users` yang dilindungi untuk administrator bot guna melihat statistik penggunaan.
-   **⚙️ Asinkron & Modular**: Dibangun dengan kerangka kerja asinkron modern dari `python-telegram-bot` dan struktur modular yang bersih untuk pemeliharaan yang mudah.

---

## Memulai

Ikuti petunjuk ini untuk menjalankan salinan lokal proyek ini.

### Prasyarat

-   Python 3.8+
-   Git
-   Token Bot Telegram dari **BotFather**
-   Kunci API GroqCloud dari **Groq**

### Instalasi

1.  **Kloning repositori:**
    ```bash
    git clone https://github.com/ATLzzzz/InsightDoc_Bot.git
    cd InsightDoc_Bot
    ```

2.  **Buat lingkungan virtual (disarankan):**
    ```bash
    # Untuk Windows
    python -m venv venv
    .\venv\Scripts\activate

    # Untuk macOS/Linux
    python3 -m venv venv
    source venv/bin/activate
    ```

3.  **Instal dependensi:**
    Proyek ini menggunakan pustaka `filelock`. Pastikan untuk menginstalnya bersama dengan paket lain dari `requirements.txt`.
    ```bash
    pip install -r requirements.txt
    pip install filelock
    ```

4.  **Konfigurasi Variabel Lingkungan:**
    Bot ini memerlukan tiga kunci rahasia. Cara terbaik untuk mengelolanya adalah dengan berkas `.env`.

    a. Buat berkas bernama `.env` di direktori utama proyek.

    b. Tambahkan konten berikut ke dalamnya, ganti placeholder dengan kredensial Anda yang sebenarnya:
    ```env
    TELEGRAM_TOKEN="TOKEN_TELEGRAM_ANDA_DI_SINI"
    GROQ_API_KEY="KUNCI_API_GROQ_ANDA_DI_SINI"
    ADMIN_ID="ID_TELEGRAM_NUMERIK_ANDA_DI_SINI"
    ```
    *(Untuk menggunakan berkas `.env`, Anda perlu menginstal `python-dotenv` (`pip install python-dotenv`) dan menambahkan `from dotenv import load_dotenv` serta `load_dotenv()` di bagian atas berkas `config.py` Anda).*

---

## Penggunaan

Setelah instalasi dan konfigurasi selesai, jalankan skrip utama untuk memulai bot:

```bash
python main.py
