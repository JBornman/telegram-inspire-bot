from telegram import Update
from telegram.ext import Updater, CommandHandler, CallbackContext
from imagefetch import fetchimage
from imagemodify import modifyimage


def hello(update: Update, context: CallbackContext) -> None:
    update.message.reply_text(f'Hello {update.effective_user.first_name}')


def fetch(update: Update, context: CallbackContext) -> None:
    fetchimage('Nature')


def mod(update: Update, context: CallbackContext) -> None:
    modifyimage('some quote', '-Some Guy')


def gen(update: Update, context: CallbackContext) -> None:
    fetchimage('Nature')
    modifyimage('some quote', '-Some Guy')


updater = Updater('<Token>')

updater.dispatcher.add_handler(CommandHandler('hello', hello))
updater.dispatcher.add_handler(CommandHandler('Fetch', fetch))
updater.dispatcher.add_handler(CommandHandler('Mod', mod))
updater.dispatcher.add_handler(CommandHandler('Gen', gen))

updater.start_polling()
updater.idle()
