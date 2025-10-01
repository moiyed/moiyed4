from dotenv import load_dotenv
load_dotenv()
import os
from twelvedata import TDClient
from telegram.ext import Application, CommandHandler, ContextTypes
import asyncio

# جلب المتغيرات من .env
api_key = os.environ.get('TWELVE_DATA_API_KEY')
risk_percent = os.environ.get('RISK_PERCENT', '1')
telegram_token = os.environ.get('TELEGRAM_TOKEN')

# تهيئة Twelve Data
td = TDClient(apikey=api_key)

# تهيئة البوت
app = Application.builder().token(telegram_token).build()

# قاموس لتتبع المشتركين
subscribed_users = {}

# دالة الاشتراك
async def start(update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribed_users[chat_id] = True
    await context.bot.send_message(chat_id=chat_id, text=f"تم الاشتراك! سأرسل تحليلًا تلقائيًا. Chat ID: {chat_id}")
    context.job_queue.run_repeating(check_trade, interval=300, first=0, data=chat_id)

# دالة التحليل
async def check_trade(context: ContextTypes.DEFAULT_TYPE):
    chat_id = context.job.data
    if chat_id in subscribed_users:
        try:
            response = td.time_series(symbol="EUR/USD", interval="1h", outputsize=5).as_json()
            if response and 'values' in response and response['values']:
                current_close = float(response['values'][0]['close'])
                if current_close > 1.1740:
                    decision = "اشتري (صفقة رابحة محتملة)"
                    await context.bot.send_message(chat_id=chat_id, text=f"تحليل: EUR/USD Close: {current_close}, قرار: {decision}, Risk: {risk_percent}%")
        except Exception as e:
            await context.bot.send_message(chat_id=chat_id, text=f"خطأ: {str(e)}")

# إضافة الأوامر
app.add_handler(CommandHandler("start", start))

# تشغيل البوت
app.run_polling(poll_interval=0.5, timeout=10, drop_pending_updates=True)
