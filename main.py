from dotenv import load_dotenv
load_dotenv()
import os
from twelvedata import TDClient
from telegram.ext import Updater, CommandHandler, JobQueue

# جلب المتغيرات من .env
api_key = os.environ.get('TWELVE_DATA_API_KEY')
risk_percent = os.environ.get('RISK_PERCENT', '1')
telegram_token = os.environ.get('TELEGRAM_TOKEN')

# تهيئة Twelve Data
td = TDClient(apikey=api_key)

# تهيئة البوت
updater = Updater(telegram_token)
dp = updater.dispatcher
job_queue = updater.job_queue
subscribed_users = {}

# دالة الاشتراك
def start(bot, update):
    chat_id = update.message.chat_id
    subscribed_users[chat_id] = True
    bot.send_message(chat_id=chat_id, text=f"تم الاشتراك! سأرسل تحليلًا تلقائيًا. Chat ID: {chat_id}")
    job_queue.run_repeating(check_trade, interval=300, context=chat_id)

# دالة التحليل
def check_trade(bot, job):
    chat_id = job.context
    if chat_id in subscribed_users:
        try:
            response = td.time_series(symbol="EUR/USD", interval="1h", outputsize=5).as_json()
            if response and 'values' in response and response['values']:
                current_close = float(response['values'][0]['close'])
                if current_close > 1.1740:
                    decision = "اشتري (صفقة رابحة محتملة)"
                    bot.send_message(chat_id=chat_id, text=f"تحليل: EUR/USD Close: {current_close}, قرار: {decision}, Risk: {risk_percent}%")
        except Exception as e:
            bot.send_message(chat_id=chat_id, text=f"خطأ: {str(e)}")

# إضافة الأوامر
dp.add_handler(CommandHandler("start", start))

# تشغيل البوت
updater.start_polling()
updater.idle()
