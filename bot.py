from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from imagefetch import FetchImage
from imagemodify import ModifyImage


def hello(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Hello {update.effective_user.first_name}')
    
def fetch(update: Update, context: CallbackContext) -> None:
    FetchImage('Nature')
    
def mod(update: Update, context: CallbackContext) -> None:
    ModifyImage('some quote','-Some Guy')

updater = Updater('<Bot Token Here>')

updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('Fetch', fetch))
updater.dispatcher.add_handler(CommandHandler('Mod', mod))

updater.start_polling()
updater.idle()
