# bot_handlers.py
import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes
from telegram.constants import ParseMode

# Import fungsi dari modul lain
from config import ADMIN_ID, MAX_CHUNK_SIZE
from utils import extract_text, split_text_into_chunks, analyze_title, generate_diff_report
from ai_service import correct_and_classify_text
from user_manager import load_user_data, track_user

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menampilkan menu utama."""
    user = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("🏛️ Dokumen DMT", callback_data='mode_dmt')],
        [InlineKeyboardButton("📄 Dokumen Umum", callback_data='mode_umum')],
        [InlineKeyboardButton("ℹ️ Bantuan", callback_data='show_help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_message = f"Halo, {user}! 👋\n\nSilakan pilih jenis dokumen yang ingin Anda proses."
    
    # Edit pesan jika berasal dari callback query, atau kirim baru jika dari /start
    if update.callback_query:
        await update.callback_query.message.edit_text(welcome_message, reply_markup=reply_markup)
    else:
        await update.message.reply_text(welcome_message, reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menampilkan pesan bantuan."""
    help_text = (
        "📘 *Panduan Penggunaan Bot*\n\n"
        "1.  Pilih mode (*Dokumen DMT* atau *Dokumen Umum*) dari menu utama.\n"
        "2.  Kirimkan file dokumen Anda (`.txt`, `.pdf`, atau `.docx`).\n"
        "3.  Bot akan menganalisis, mengoreksi, dan mengklasifikasikan dokumen Anda.\n"
        "4.  Anda akan menerima file `.txt` hasil koreksi beserta laporan perubahannya."
    )
    keyboard = [[InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.message.edit_text(help_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)
    else:
        await update.message.reply_text(help_text, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)


async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani penekanan tombol inline."""
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == 'mode_dmt':
        context.user_data['mode'] = 'DMT'
        await query.edit_message_text(text="Mode *Dokumen DMT* dipilih.\n\nSilakan kirimkan dokumen Anda.", parse_mode=ParseMode.MARKDOWN)
    elif data == 'mode_umum':
        context.user_data['mode'] = 'Umum'
        await query.edit_message_text(text="Mode *Dokumen Umum* dipilih.\n\nSilakan kirimkan dokumen Anda.", parse_mode=ParseMode.MARKDOWN)
    elif data == 'show_help':
        await help_command(update, context)
    elif data == 'back_to_menu':
        await start(update, context)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Memproses dokumen yang dikirim oleh pengguna."""
    mode = context.user_data.get('mode')
    if not mode:
        await update.message.reply_text("Silakan pilih mode terlebih dahulu dengan perintah /start.")
        return

    track_user(update.effective_user, mode)
    doc = update.message.document
    file_path = f"download_{doc.file_name}"
    
    processing_message = await update.message.reply_text(
        f"✅ Dokumen `{doc.file_name}` diterima. Memproses dalam mode *{mode}*...",
        parse_mode=ParseMode.MARKDOWN
    )

    try:
        file_data = await context.bot.get_file(doc.file_id)
        await file_data.download_to_drive(file_path)

        original_text, error_message = extract_text(file_path)
        if error_message or not original_text or not original_text.strip():
            await processing_message.edit_text(error_message or "❌ Dokumen kosong atau tidak dapat dibaca.")
            return

        text_chunks = split_text_into_chunks(original_text, MAX_CHUNK_SIZE)
        corrected_chunks = []
        final_classification = "Tidak Diketahui"

        for i, chunk in enumerate(text_chunks):
            await processing_message.edit_text(
                f"🧠 Menganalisis dengan AI (Mode: {mode})... Bagian {i + 1} dari {len(text_chunks)}."
            )
            is_first = (i == 0)
            ai_result = correct_and_classify_text(chunk, is_first_chunk=is_first, mode=mode)

            if "error" in ai_result:
                await processing_message.edit_text(
                    f"❌ Error pada bagian {i+1}:\n`{ai_result['error']}`",
                    parse_mode=ParseMode.MARKDOWN
                )
                return

            corrected_chunks.append(ai_result.get("koreksi_teks", chunk))
            if is_first:
                final_classification = ai_result.get("klasifikasi", "Tidak Diketahui")

        full_corrected_text = "".join(corrected_chunks)

        # ---- FITUR BARU: Buat dan Kirim Laporan Perubahan ----
        diff_report = generate_diff_report(original_text, full_corrected_text)
        await update.message.reply_text(diff_report, parse_mode=ParseMode.MARKDOWN)
        # ----------------------------------------------------

        result_message = (
            f"🎉 *Analisis Selesai!*\n\n"
            f"📎 *File Asli:* `{doc.file_name}`\n"
            f"🏷️ *Hasil Klasifikasi ({mode}):* *{final_classification}*\n\n"
            "Dokumen yang telah dikoreksi akan dikirimkan sesaat lagi."
        )
        await processing_message.edit_text(result_message, parse_mode=ParseMode.MARKDOWN)

        corrected_filename = f"corrected_{os.path.splitext(doc.file_name)[0]}.txt"
        with open(corrected_filename, "w", encoding="utf-8") as f:
            f.write(full_corrected_text)
        
        with open(corrected_filename, "rb") as f:
            await context.bot.send_document(
                chat_id=update.effective_chat.id,
                document=f,
                filename=corrected_filename,
                caption="📄 Ini adalah versi final dari dokumen yang sudah dikoreksi."
            )
        os.remove(corrected_filename)

    except Exception as e:
        logger.error(f"❌ Error saat proses handle_document: {e}")
        await processing_message.edit_text(f"❌ Terjadi kesalahan tak terduga: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


async def check_title(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menganalisis judul yang diberikan setelah perintah /checktitle."""
    if not context.args:
        await update.message.reply_text(
            "Silakan masukkan judul setelah perintah /checktitle.\n\n"
            "Contoh: `/checktitle Analisis Sentimen pada Ulasan Produk E-commerce Menggunakan Metode Naive Bayes`",
            parse_mode=ParseMode.MARKDOWN
        )
        return
    title = " ".join(context.args)
    feedback = analyze_title(title)
    await update.message.reply_text(feedback, parse_mode=ParseMode.MARKDOWN)


async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """(Admin only) Menampilkan data pengguna bot."""
    if update.effective_user.id != ADMIN_ID:
        await update.message.reply_text("⛔ Anda tidak memiliki izin untuk menggunakan perintah ini.")
        return
    
    users = load_user_data()
    if not users:
        await update.message.reply_text("Belum ada pengguna yang tercatat.")
        return

    message = "👥 *Daftar Pengguna Bot*\n\n"
    for uid, data in users.items():
        username = f"(@{data['username']})" if data['username'] != 'N/A' else ""
        message += (
            f"👤 *{data['first_name']}* {username}\n"
            f"  - ID: `{uid}`\n"
            f"  - Mode Terakhir: {data.get('last_mode', 'N/A')}\n"
            f"  - Jumlah Penggunaan: {data['usage_count']} kali\n"
            f"  - Terakhir Aktif: {data['last_used']}\n\n"
        )
    await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)


async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Menangani pesan teks yang bukan perintah."""
    await update.message.reply_text("Maaf, saya hanya bisa memproses dokumen. Silakan gunakan /start untuk memulai.")