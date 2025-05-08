# bot.py
from flask import Flask, request
import asyncio
from telegram import Update, InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, ConversationHandler, ContextTypes, filters
from texts import texts
from dotenv import load_dotenv
import os
import yt_dlp
import traceback 
import logging

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# Load environment variables
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')

# States
ASK_FOR_LINK, ASK_FOR_QUALITY = range(2)

# Start Handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data='en')],
        [InlineKeyboardButton("🇸🇦 العربية", callback_data='ar')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(texts['start_language_prompt']['en'], reply_markup=reply_markup)

# Language Chooser
async def choose_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    lang = query.data
    context.user_data['language'] = lang

    await query.message.reply_text(texts['greeting'][lang])

    # Now show main reply menu (Download Video, Cancel)
    reply_keyboard = [
        ["Download Video 🎥"] if lang == 'en' else ["تحميل فيديو 🎥"],
        ["Cancel ❌"] if lang == 'en' else ["❌ إلغاء"]
    ]
    markup = ReplyKeyboardMarkup(reply_keyboard, resize_keyboard=True)

    await query.message.reply_text(
        "🔽 Choose an action:" if lang == 'en' else "🔽 اختر وش تبي تسوي:",
        reply_markup=markup
    )


# Change Language Handler
async def change_language(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data='en')],
        [InlineKeyboardButton("🇸🇦 العربية", callback_data='ar')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    lang = context.user_data.get('language', 'en')
    await update.message.reply_text(texts['start_language_prompt'][lang], reply_markup=reply_markup)

# Download Command or Button
async def download_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('language', 'en')
    await update.message.reply_text(texts['ask_link'][lang])
    return ASK_FOR_LINK

async def error_handler(update, context):
    logging.error("🚨 Exception while handling an update:", exc_info=context.error)


    # Optionally log traceback:
    traceback.print_exception(type(context.error), context.error, context.error.__traceback__)

# Handle User Link
async def handle_link(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text
    context.user_data['url'] = url

    lang = context.user_data.get('language', 'en')

    # Show quality choices
    keyboard = [
        [InlineKeyboardButton("HD 🔥", callback_data='hd')],
        [InlineKeyboardButton("جودة عادية 📼" if lang == 'ar' else "SD 📼", callback_data='sd')],
        [InlineKeyboardButton("صوت بس 🎵" if lang == 'ar' else "Audio Only 🎵", callback_data='audio')],
        [InlineKeyboardButton("❌ إلغاء" if lang == 'ar' else "❌ Cancel", callback_data='cancel')],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await update.message.reply_text(texts['quality_prompt'][lang], reply_markup=reply_markup)
    return ASK_FOR_QUALITY

# Handle Quality Choice
async def handle_quality_choice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    choice = None

    if update.callback_query:
        query = update.callback_query
        await query.answer()

        choice = query.data
        lang = context.user_data.get('language', 'en')

        await query.message.reply_text(texts['downloading'][lang])

    url = context.user_data.get('url')

    # yt-dlp options
    ydl_opts = {
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'merge_output_format': 'mp4',
        'postprocessors': [{
            'key': 'FFmpegVideoConvertor',
            'preferedformat': 'mp4',  # this is intentionally misspelled due to yt-dlp
        }],
        'postprocessor_args': [
            '-c:v', 'libx264',
            '-preset', 'veryfast',
            '-crf', '23',
            '-c:a', 'aac'
        ]
    }

    if choice in ['hd', 'HD 🔥']:
        ydl_opts['format'] = 'bestvideo+bestaudio/best'
    elif choice in ['sd', 'جودة عادية 📼', 'SD 📼']:
        ydl_opts['format'] = 'worstvideo+worstaudio/worst'
    elif choice in ['audio', 'صوت بس 🎵', 'Audio Only 🎵']:
        ydl_opts['format'] = 'bestaudio/best'
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]
    elif choice in ['cancel', '❌ إلغاء', '❌ Cancel']:
        await query.message.reply_text(texts['cancelled'][lang])
        return ConversationHandler.END

    try:
        os.makedirs('downloads', exist_ok=True)

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

            if choice in ['audio', 'صوت بس 🎵', 'Audio Only 🎵']:
                filename = filename.rsplit('.', 1)[0] + ".mp3"

        file_size = os.path.getsize(filename) / (1024 * 1024)  # MB

        if file_size > 50:
            await query.message.reply_text(texts['too_large'][lang])
            os.remove(filename)
            return ConversationHandler.END

        await query.message.reply_text(texts['sending'][lang])

        with open(filename, 'rb') as file_to_send:
            if choice in ['audio', 'صوت بس 🎵', 'Audio Only 🎵']:
                await query.message.reply_audio(file_to_send)
            else:
                await query.message.reply_video(file_to_send)

        await query.message.reply_text(texts['download_complete'][lang])

        os.remove(filename)
        return ConversationHandler.END

    except Exception as e:
        print("❌ Exception occurred during video processing:")
        traceback.print_exc()  # Shows full error in console
        await query.message.reply_text(texts['error'][lang])
        return ConversationHandler.END

# Cancel Handler (in case of message cancel)
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = context.user_data.get('language', 'en')
    await update.message.reply_text(texts['cancelled'][lang])
    return ConversationHandler.END

# Main
# def main():
#     application = ApplicationBuilder().token(BOT_TOKEN).build()

#     conv_handler = ConversationHandler(
#         entry_points=[
#             CommandHandler('download', download_command),
#             MessageHandler(filters.Regex('^تحميل فيديو 🎥$'), download_command),
#             MessageHandler(filters.Regex('^Download Video 🎥$'), download_command),
#         ],
#         states={
#             ASK_FOR_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link)],
#             ASK_FOR_QUALITY: [
#                 CallbackQueryHandler(handle_quality_choice),
#                 MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quality_choice),
#             ],
#         },
#         fallbacks=[
#             CommandHandler('cancel', cancel),
#             MessageHandler(filters.Regex('^❌ إلغاء$'), cancel),
#             MessageHandler(filters.Regex('^❌ Cancel$'), cancel),
#         ],
#         per_message=True,
#     )

#     application.add_handler(CommandHandler('start', start))
#     application.add_handler(CommandHandler('language', change_language))
#     application.add_handler(conv_handler)
#     application.add_error_handler(error_handler)
#     application.add_handler(CallbackQueryHandler(choose_language, pattern='^(en|ar)$'))

#     application.run_polling()

# if __name__ == '__main__':
#     main()


app = Flask(__name__)
application = ApplicationBuilder().token(BOT_TOKEN).build()

# === Register your handlers here, same as before ===
conv_handler = ConversationHandler(
    entry_points=[
        CommandHandler('download', download_command),
        MessageHandler(filters.Regex('^تحميل فيديو 🎥$'), download_command),
        MessageHandler(filters.Regex('^Download Video 🎥$'), download_command),
    ],
    states={
        ASK_FOR_LINK: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_link)],
        ASK_FOR_QUALITY: [
            CallbackQueryHandler(handle_quality_choice),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_quality_choice),
        ],
    },
    fallbacks=[
        CommandHandler('cancel', cancel),
        MessageHandler(filters.Regex('^❌ إلغاء$'), cancel),
        MessageHandler(filters.Regex('^❌ Cancel$'), cancel),
    ],
    per_message=True,
)

application.add_handler(CommandHandler('start', start))
application.add_handler(CommandHandler('language', change_language))
application.add_handler(conv_handler)
application.add_error_handler(error_handler)
application.add_handler(CallbackQueryHandler(choose_language, pattern='^(en|ar)$'))


@app.route('/webhook', methods=['POST'])
def webhook():
    update = Update.de_json(request.get_json(force=True), application.bot)

    async def handle():
        if not application._initialized:
            await application.initialize()
        await application.process_update(update)

    asyncio.run(handle())
    return 'ok', 200


@app.route('/')
def index():
    return "🤖 Telegram bot webhook is live!"

async def set_webhook():
    await application.bot.delete_webhook(drop_pending_updates=True)
    await application.bot.set_webhook(f"https://{WEBHOOK_URL}/webhook")


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(set_webhook())
    app.run(host='0.0.0.0', port=8000)