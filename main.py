from dotenv import load_dotenv
load_dotenv()
import os
from twelvedata import TDClient
from telegram.ext import Updater, CommandHandler, JobQueue

api_key = os.environ.get('TWELVE_DATA_API_KEY')
risk_percent = os.environ.get('RISK_PERCENT', '1')
telegram_token = os.environ.get('TELEGRAM_TOKEN')

td = TDClient(apikey=api_key)
updater = Updater(telegram_token, use_context=True)  # مناسب للإصدار 22.5
dp = updater.dispatcher
job_queue = updater.job_queue
subscribed_users = {}  # قاموس لتتبع المشتركين

# دالة الاشتراك
def start(update, context):
    chat_id = update.message.chat_id
    subscribed_users[chat_id] = True
    context.bot.send_message(chat_id=chat_id, text=f"تم الاشتراك! سأرسل لك تحليلًا تلقائيًا لأي صفقة رابحة. Chat ID: {chat_id}")
    context.job_queue.run_repeating(check_profitable_trade, interval=300, first=0, context=chat_id)

# دالة التحليل لتحديد صفقة رابحة
def check_profitable_trade(context):
    chat_id = context.job.context
    if chat_id in subscribed_users:
        try:
            response = td.time_series(symbol="EUR/USD", interval="1h", outputsize=5).as_json()
            if isinstance(response, tuple) and len(response) > 0 and isinstance(response[0], dict):
                data = [response[0]]  # تحويل الـ dict لـ list
            else:
                data = []
            if len(data) >= 1:
                current_close = float(data[0]['close'])
                if current_close > 1.1740:
                    decision = "اشتري (صفقة رابحة محتملة)"
                    context.bot.send_message(chat_id=chat_id, text=f"تحليل: EUR/USD Close: {current_close}, قرار: {decision}, Risk: {risk_percent}%")
        except Exception as e:
            context.bot.send_message(chat_id=chat_id, text=f"خطأ في التحليل: {e}")

# سجل الأوامر
dp.add_handler(CommandHandler("start", start))

# شغل البوت
updater.start_polling()
updater.idle()