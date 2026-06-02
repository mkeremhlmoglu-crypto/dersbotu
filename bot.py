import os
import easyocr
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
import google.generativeai as genai

TOKEN = os.getenv("TOKEN")
GEMINI_KEY = os.getenv("GEMINI_KEY")

genai.configure(api_key=GEMINI_KEY)
model = genai.GenerativeModel("gemini-1.5-flash")

reader = easyocr.Reader(['tr', 'en'])

def ocr(path):
    return "\n".join(reader.readtext(path, detail=0))

async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    photo = update.message.photo[-1]
    file = await photo.get_file()

    path = "soru.jpg"
    await file.download_to_drive(path)

    text = ocr(path)

    if not text.strip():
        await update.message.reply_text("📸 Yazı okunamadı")
        return

    prompt = f"""
Sen bir öğretmensin. Bu soruyu adım adım çöz:

{text}
"""

    response = model.generate_content(prompt)

    await update.message.reply_text(response.text)

app = Application.builder().token(TOKEN).build()

app.add_handler(MessageHandler(filters.PHOTO, handle_photo))

app.run_polling()
