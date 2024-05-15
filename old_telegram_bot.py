from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler,MessageHandler,filters
import os
import signal
import request

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

async def stop(bot, update):
    os.kill(os.getpid(), signal.SIGINT)
    
async def run(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text_caps = ' '.join(context.args).upper()
    await context.bot.send_message(chat_id=update.effective_chat.id, text=text_caps)
    
def init_bot(tgbot_token):
    application = ApplicationBuilder().token(tgbot_token).build()
    
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('stop', stop))
    application.add_handler(CommandHandler('run', run))
    application.run_polling()

if __name__ == '__main__':
    try:
        init_bot(os.environ["tgbot_token"])
    except KeyError as e:
        print(e)
