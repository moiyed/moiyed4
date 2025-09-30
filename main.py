from dotenv import load_dotenv
load_dotenv()
import os
from twelvedata import TDClient
from telegram.ext import Updater, CommandHandler, Queue  # أضفنا Queue

api_key = os.environ.get('TWELVE_DATA_API_KEY')
risk_percent = os.environ.get('RISK_PERCENT', '1')
telegram_token = os.environ.get('TELEGRAM_TOKEN')

td = TDClient(apikey=api_key)
update_queue = Queue()  # أنشئ كائن Queue
updater = Updater(telegram_token, update_queue=update_queue)  # أضف update_queue
dp = updater.dispatcher
subscribed_users = {}

def start(update, context):
    chat_id = update.message.chat_id
    subscribed_users[chat_id] = True
    context.bot.send_message(chat_id=chat_id, text=f"تم الاشتراك! سأرسل لك تحليلًا تلقائيًا. Chat ID: {chat_id}")
    updater.job_queue.run_repeating(check_profitable_trade, interval=300, context=chat_id)

def check_profitable_trade(context):
    chat_id = context.job.context
    if chat_id in subscribed_users:
        try:
            response = td.time_series(symbol="EUR/USD", interval="1h", outputsize=5).as_json()
            if response and isinstance(response[0], dict):
                current_close = float(response[0]['close'])
                if current_close > 1.1740:
                    decision = "اشتري (صفقة رابحة محتملة)"
                    context.bot.send_message(chat_id=chat_id, text=f"تحليل: EUR/USD Close: {current_close}, قرار: {decision}, Risk: {risk_percent}%")
        except Exception as e:
            context.bot.send_message(chat_id=chat_id, text=f"خطأ: {e}")

dp.add_handler(CommandHandler("start", start))
updater.start_polling()
updater.idle()
