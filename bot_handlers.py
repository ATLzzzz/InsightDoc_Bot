<<<<<<< HEAD
# bot_handlers.py
import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

# Import functions from other modules
from config import ADMIN_ID, MAX_CHUNK_SIZE
from utils import extract_text, split_text_into_chunks
from ai_service import correct_and_classify_text
from user_manager import load_user_data, track_user

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("🏛️ Dokumen DMT", callback_data='mode_dmt')],
        [InlineKeyboardButton("📄 Dokumen Umum", callback_data='mode_umum')],
        [InlineKeyboardButton("ℹ️ Bantuan", callback_data='show_help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_message = f"Halo, {user}! 👋\n\nSilakan pilih jenis dokumen yang ingin Anda proses."
    if update.callback_query:
        await update.callback_query.message.edit_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "📘 *Panduan Penggunaan Bot*\n\n1. Pilih mode 'Dokumen DMT' atau 'Dokumen Umum' dari menu utama.\n2. Kirimkan file `.txt`, `.pdf`, atau `.docx`.\n3. Saya akan membalas dengan hasil analisis sesuai mode yang dipilih."
    keyboard = [[InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.message.edit_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)


async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == 'mode_dmt':
        context.user_data['mode'] = 'DMT'
        await query.edit_message_text(text="Mode *Dokumen DMT* dipilih.\n\nSekarang, silakan kirimkan dokumen Anda.", parse_mode='Markdown')
    elif data == 'mode_umum':
        context.user_data['mode'] = 'Umum'
        await query.edit_message_text(text="Mode *Dokumen Umum* dipilih.\n\nSekarang, silakan kirimkan dokumen Anda.", parse_mode='Markdown')
    elif data == 'show_help':
        await help_command(update, context)
    elif data == 'back_to_menu':
        await start(update, context)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get('mode')
    if not mode:
        await update.message.reply_text("Silakan pilih mode terlebih dahulu dengan mengetik /start.")
        return
    
    track_user(update.effective_user, mode)
    file = update.message.document
    file_path = f"download_{file.file_name}"
    processing_message = await update.message.reply_text(f"✅ Dokumen `{file.file_name}` diterima. Memproses dalam mode *{mode}*...", parse_mode='Markdown')

    try:
        # UPDATED FILE DOWNLOAD METHOD
        file_data = await context.bot.get_file(file.file_id)
        await file_data.download_to_path(file_path)

        text, error_message = extract_text(file_path)
        if error_message or not text or not text.strip():
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_message.message_id, text=error_message or "❌ Dokumen kosong.")
            return

        text_chunks = split_text_into_chunks(text, MAX_CHUNK_SIZE)
        
        # EFFICIENT STRING HANDLING
        corrected_chunks = []
        final_classification = "Tidak Diketahui"

        for i, chunk in enumerate(text_chunks):
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_message.message_id, text=f"🧠 Menganalisis dengan AI (Mode: {mode})... Bagian {i + 1} dari {len(text_chunks)}.")
            is_first = (i == 0)
            ai_result = correct_and_classify_text(chunk, is_first_chunk=is_first, mode=mode)
            
            if "error" in ai_result:
                await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_message.message_id, text=f"❌ Error pada bagian {i+1}:\n`{ai_result['error']}`", parse_mode='Markdown')
                return

            corrected_chunks.append(ai_result.get("koreksi_teks", chunk))
            if is_first:
                final_classification = ai_result.get("klasifikasi", "Tidak Diketahui")
        
        full_corrected_text = "".join(corrected_chunks)

        result_message = (
            f"🎉 *Analisis Selesai!*\n\n"
            f"📎 *File Asli:* `{file.file_name}`\n"
            f"🏷️ *Hasil Klasifikasi ({mode}):* *{final_classification}*\n\n"
            "Dokumen yang telah dikoreksi akan dikirimkan sesaat lagi."
        )
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_message.message_id, text=result_message, parse_mode='Markdown')

        corrected_filename = f"corrected_{os.path.splitext(file.file_name)[0]}.txt"
        with open(corrected_filename, "w", encoding="utf-8") as f:
            f.write(full_corrected_text)
        with open(corrected_filename, "rb") as f:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=f, filename=corrected_filename, caption="📄 Dokumen versi final yang sudah dikoreksi.")
        os.remove(corrected_filename)

    except Exception as e:
        logger.error(f"❌ Error saat proses handle_document: {e}")
        await update.message.reply_text(f"❌ Terjadi kesalahan tak terduga: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Maaf, saya tidak mengerti. Silakan gunakan /start untuk memilih mode.")


async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        message += f"👤 *{data['first_name']}* {username}\n  - ID: `{uid}`\n  - Mode Terakhir: {data.get('last_mode', 'N/A')}\n  - Jumlah Penggunaan: {data['usage_count']} kali\n  - Terakhir Aktif: {data['last_used']}\n\n"
=======
# bot_handlers.py
import os
import logging
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import ContextTypes

# Import functions from other modules
from config import ADMIN_ID, MAX_CHUNK_SIZE
from utils import extract_text, split_text_into_chunks
from ai_service import correct_and_classify_text
from user_manager import load_user_data, track_user

logger = logging.getLogger(__name__)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name
    keyboard = [
        [InlineKeyboardButton("🏛️ Dokumen DMT", callback_data='mode_dmt')],
        [InlineKeyboardButton("📄 Dokumen Umum", callback_data='mode_umum')],
        [InlineKeyboardButton("ℹ️ Bantuan", callback_data='show_help')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_message = f"Halo, {user}! 👋\n\nSilakan pilih jenis dokumen yang ingin Anda proses."
    if update.callback_query:
        await update.callback_query.message.edit_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text(welcome_message, parse_mode='Markdown', reply_markup=reply_markup)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    help_text = "📘 *Panduan Penggunaan Bot*\n\n1. Pilih mode 'Dokumen DMT' atau 'Dokumen Umum' dari menu utama.\n2. Kirimkan file `.txt`, `.pdf`, atau `.docx`.\n3. Saya akan membalas dengan hasil analisis sesuai mode yang dipilih."
    keyboard = [[InlineKeyboardButton("⬅️ Kembali ke Menu Utama", callback_data='back_to_menu')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    if update.callback_query:
        await update.callback_query.message.edit_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)
    else:
        await update.message.reply_text(help_text, parse_mode='Markdown', reply_markup=reply_markup)


async def handle_button_press(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    if data == 'mode_dmt':
        context.user_data['mode'] = 'DMT'
        await query.edit_message_text(text="Mode *Dokumen DMT* dipilih.\n\nSekarang, silakan kirimkan dokumen Anda.", parse_mode='Markdown')
    elif data == 'mode_umum':
        context.user_data['mode'] = 'Umum'
        await query.edit_message_text(text="Mode *Dokumen Umum* dipilih.\n\nSekarang, silakan kirimkan dokumen Anda.", parse_mode='Markdown')
    elif data == 'show_help':
        await help_command(update, context)
    elif data == 'back_to_menu':
        await start(update, context)


async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE):
    mode = context.user_data.get('mode')
    if not mode:
        await update.message.reply_text("Silakan pilih mode terlebih dahulu dengan mengetik /start.")
        return
    
    track_user(update.effective_user, mode)
    file = update.message.document
    file_path = f"download_{file.file_name}"
    processing_message = await update.message.reply_text(f"✅ Dokumen `{file.file_name}` diterima. Memproses dalam mode *{mode}*...", parse_mode='Markdown')

    try:
        # UPDATED FILE DOWNLOAD METHOD
        file_data = await context.bot.get_file(file.file_id)
        await file_data.download_to_path(file_path)

        text, error_message = extract_text(file_path)
        if error_message or not text or not text.strip():
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_message.message_id, text=error_message or "❌ Dokumen kosong.")
            return

        text_chunks = split_text_into_chunks(text, MAX_CHUNK_SIZE)
        
        # EFFICIENT STRING HANDLING
        corrected_chunks = []
        final_classification = "Tidak Diketahui"

        for i, chunk in enumerate(text_chunks):
            await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_message.message_id, text=f"🧠 Menganalisis dengan AI (Mode: {mode})... Bagian {i + 1} dari {len(text_chunks)}.")
            is_first = (i == 0)
            ai_result = correct_and_classify_text(chunk, is_first_chunk=is_first, mode=mode)
            
            if "error" in ai_result:
                await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_message.message_id, text=f"❌ Error pada bagian {i+1}:\n`{ai_result['error']}`", parse_mode='Markdown')
                return

            corrected_chunks.append(ai_result.get("koreksi_teks", chunk))
            if is_first:
                final_classification = ai_result.get("klasifikasi", "Tidak Diketahui")
        
        full_corrected_text = "".join(corrected_chunks)

        result_message = (
            f"🎉 *Analisis Selesai!*\n\n"
            f"📎 *File Asli:* `{file.file_name}`\n"
            f"🏷️ *Hasil Klasifikasi ({mode}):* *{final_classification}*\n\n"
            "Dokumen yang telah dikoreksi akan dikirimkan sesaat lagi."
        )
        await context.bot.edit_message_text(chat_id=update.effective_chat.id, message_id=processing_message.message_id, text=result_message, parse_mode='Markdown')

        corrected_filename = f"corrected_{os.path.splitext(file.file_name)[0]}.txt"
        with open(corrected_filename, "w", encoding="utf-8") as f:
            f.write(full_corrected_text)
        with open(corrected_filename, "rb") as f:
            await context.bot.send_document(chat_id=update.effective_chat.id, document=f, filename=corrected_filename, caption="📄 Dokumen versi final yang sudah dikoreksi.")
        os.remove(corrected_filename)

    except Exception as e:
        logger.error(f"❌ Error saat proses handle_document: {e}")
        await update.message.reply_text(f"❌ Terjadi kesalahan tak terduga: {e}")
    finally:
        if os.path.exists(file_path):
            os.remove(file_path)


async def unknown_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Maaf, saya tidak mengerti. Silakan gunakan /start untuk memilih mode.")


async def show_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
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
        message += f"👤 *{data['first_name']}* {username}\n  - ID: `{uid}`\n  - Mode Terakhir: {data.get('last_mode', 'N/A')}\n  - Jumlah Penggunaan: {data['usage_count']} kali\n  - Terakhir Aktif: {data['last_used']}\n\n"
>>>>>>> 4d3658cfa924fc51dde2eb9c6b1a60c506160a54
    await update.message.reply_text(message, parse_mode='Markdown')