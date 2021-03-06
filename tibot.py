from asyncio.log import logger
import os
from turtle import up
from telegram import Bot, ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)
from imagefetch import fetchimage
from imagemodify import modifyimage
from dotenv import load_dotenv

state_quote, state_source, state_image = range(3)
quote: str = ''
source: str = ''
image_seed: str = ''
load_dotenv()

def start(update: Update, context: CallbackContext) -> int:
    """
    Initialize the conversation with the user and asks user for quote value

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        state_quote (int): status update to quote status
    """

    update.message.reply_text(
        'Hello I am TiBot the quote wallpapers generation bot, send me a plaintext quote so I can show you what I can do'
    )
    return state_quote


def again(update: Update, context: CallbackContext) -> int:
    """
    Restart the conversation with the user and asks user for quote value

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        state_quote (int): status update to quote status
    """
    update.message.reply_text('Please send me a quote')
    return state_quote


def quote(update: Update, context: CallbackContext) -> int:
    """
    Updates  global quote value and asks user for source value

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        state_source (int): status update to source status
    """
    global quote
    quote = update.message.text
    update.message.reply_text('and who said "' + quote + '"')
    return state_source


def source(update: Update, context: CallbackContext) -> int:
    """
    Updates the global source value and asks user for image search term

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        state_image (int): status update to image status
    """
    global source
    source = '-' + update.message.text
    update.message.reply_text(
        'What term should I used to search for a background image ?')
    return state_image


def image(update: Update, context: CallbackContext) -> int:
    """
    Updates the global image seed.
    Fetch the image from using imagefetch.py.
    Add the quote and source to the image using imagemodify.py.
    Send completed image to user.

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        END (int): status update to end conversation
    """
    bot = Bot(os.getenv('TOKEN'))
    global image_seed
    chat_id = update.message.chat_id
    image_seed = update.message.text
    try: # Try to get the image and map the quote
        fetchimage(image_seed)
        modifyimage(quote, source)
        bot.send_message(chat_id, 'Done please find attatched')
        bot.send_document(chat_id, open("downloads/quote.jpg", 'rb'))
        update.message.reply_text(
        'If you want to generate another image just send /quote')
        return ConversationHandler.END
    except Exception as exec: # Image not found error and loop back
        print(exec)
        bot.send_message(chat_id, 'No images with that seed, please send another seed')
        return state_image
    


def cancel(update: Update, context: CallbackContext) -> int:
    """
    Fallback method to cancel

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        END (int): status update to end conversation
    """
    user = update.message.from_user
    update.message.reply_text('Bye bye ' + user.username)
    return ConversationHandler.END


def main():
    """
    Run the main conversation handler
    """
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.getenv('TOKEN'))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler('start', start),
            # CommandHandler('quote', quote),
            # CommandHandler('source', source),
            # CommandHandler('image', image),
            CommandHandler('quote', again),
            CommandHandler('cancel', cancel)
        ],
        states={
            state_quote: [MessageHandler(Filters.text, quote)],
            state_source: [MessageHandler(Filters.text, source)],
            state_image: [MessageHandler(Filters.text, image)],
        },
        fallbacks=[CommandHandler('cancel', cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
