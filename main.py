# main.py
import logging
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler, filters, CallbackQueryHandler)

from config import TELEGRAM_TOKEN
from bot_handlers import (start, help_command, show_users, handle_button_press, handle_document, unknown_text, check_title)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """Memulai dan menjalankan bot Telegram."""
    application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("users", show_users))
    application.add_handler(CommandHandler("checktitle", check_title))
    application.add_handler(CallbackQueryHandler(handle_button_press))
    application.add_handler(MessageHandler(filters.Document.ALL, handle_document))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, unknown_text))

    logger.info("🚀 Bot aktif dan siap digunakan...")
    application.run_polling()

if __name__ == '__main__':
    main()