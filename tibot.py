import os
import io
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
    CallbackQueryHandler,
)
from dotenv import load_dotenv
from PIL import Image
from scrapers import wallhaven, bing, unsplash
import image_modify
import local_storage


# Menu enums & load vars
(
    state_quote,
    state_source,
    state_date_menu,
    state_image,
    state_img_provider,
    state_img_searchterm,
    state_done_menu,
) = range(7)  # All States of application

cbd_quote, cbd_done, cbd_change_image, cbd_new_bg_src = range(4)  # Menu options for completion menu
cbd_date_None, cbd_date_Year, cbd_date_MonthYear, cbd_date_DayMonthYear = range(4)  # Menu items for date options
cbd_src_wallhaven, cbd_src_unsplash = range(2)  # Menu items for image selection menu
load_dotenv()

# Keyboards
FinishMenuKeyboard = [
    [
        InlineKeyboardButton("Change BG Image", callback_data=str(cbd_change_image)),
        InlineKeyboardButton("New BG Source", callback_data=str(cbd_new_bg_src)),
    ],
    [
        InlineKeyboardButton("Another Quote", callback_data=str(cbd_quote)),
        InlineKeyboardButton("I'm Done", callback_data=str(cbd_done)),
    ],
]
finish_kb_markup = InlineKeyboardMarkup(FinishMenuKeyboard)

provider_keyboard = [
    [
        InlineKeyboardButton("Wallhaven", callback_data=str(cbd_src_wallhaven)),
        InlineKeyboardButton("Unsplash", callback_data=str(cbd_src_unsplash)),
    ]
]
provider_markup = InlineKeyboardMarkup(provider_keyboard)

img_search_keyboard = [
    [
        InlineKeyboardButton("Landscape", callback_data="Landscape"),
        InlineKeyboardButton("Abstract", callback_data="Abstract"),
    ],
    [InlineKeyboardButton("Bing Image of the day", callback_data="#BING#")],
]
img_search_markup = InlineKeyboardMarkup(img_search_keyboard)

# Strings
ASKFORIMAGE = "What term should I used to search for a background image?\nYou can send me a (compressed) image or choose an option below"
ASKFORPROVIDER = "Choose a provider below"
ENDCONVO = "Bye bye "
FIRSTIMAGEQUOTE = "Here you go, hot off the presses"
FINISHEDMESSAGE = "What would you like to do now?"
PLZ_WAIT_MSG = "Please wait, we are doing cool image things..."


def tele_img_convert(img: Image):
    """
    Converts PIL & telegram images to a Bytes stream which can be used by both PIL & Telegram

    Args:
        img (PIL Image): The image to be converted

    Returns:
        Image Stream (BytesIO): Bytes stream of the image
    """

    output = io.BytesIO()
    img.save(output, format="PNG")
    return output.getvalue()



def start(update: Update, context: CallbackContext) -> int:
    """
    Initialize the conversation with the user and asks the user for quote
    initiated with /start command

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        state_quote (int): return to conversation handler and wait for a quote before executing the relevant method
    """

    update.message.reply_text(
        "Hello I am TiBot, the quote wallpapers generation bot. Send me a plaintext quote so I can show you what I can do"
    )

    return state_quote



def again(update: Update, context: CallbackContext) -> int:
    """
    Restart the conversation with the user and asks the user for another quote

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        state_quote (int): return to conversation handler and wait for a quote before executing the relevant method
    """

    query = update.callback_query
    query.answer()

    context.chat_data.clear()

    query.message.edit_text("Great! Please send me a quote?")

    return state_quote



def quote(update: Update, context: CallbackContext) -> int:
    """
    Stores the quote & asks for the quote master / author

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        state_source (int): return to conversation handler and wait for a source before executing the relevant method
    """

    quote_txt = update.message.text
    context.chat_data["Quote"] = quote_txt

    # Set the image re-generation flag to false. this will be needed in the image generation methods
    context.chat_data["ChangeBG"] = False

    update.message.reply_text(f'and who said "{quote_txt}"?')
    return state_source



def source(update: Update, context: CallbackContext) -> int:
    """
    Stores the quote source (quote master / author) & asks the user for a date

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        state_date_menu (int): return to conversation handler and wait for a date before executing the relevant method
    """

    context.chat_data["Source"] = update.message.text

    date_keyboard = [
        [
            InlineKeyboardButton("None", callback_data=str(cbd_date_None)),
            InlineKeyboardButton("Year", callback_data=str(cbd_date_Year)),
        ],
        [
            InlineKeyboardButton("Month & Year", callback_data=str(cbd_date_MonthYear)),
            InlineKeyboardButton(
                "Day, Month & Year", callback_data=str(cbd_date_DayMonthYear)
            ),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(date_keyboard)

    update.message.reply_text(
        "Would you like to add a date?\nYou can choose a preset or type a date if its not from today",
        reply_markup=reply_markup,
    )
    return state_date_menu



def get_date_string(date_callback_data):
    """
    Returns the current date in the format specified by the on screen options

    Args:
        date_callback_data (int): Value provided by the on screen options

    Returns:
        date (str): Date in the requested format
    """

    current_date = datetime.now()

    if date_callback_data == "0":
        return None
    elif date_callback_data == "1":
        return current_date.strftime("%Y")
    elif date_callback_data == "2":
        return current_date.strftime("%B %Y")
    elif date_callback_data == "3":
        return current_date.strftime("%-m %B %Y")



def date_selection(update: Update, context: CallbackContext) -> int:
    """
    Stores the date string (that was generated according to the requested format), then asks the user for an image or search term

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        state_image (int): return to conversation handler and wait for an image or search term before executing the relevant method
    """

    query = update.callback_query
    query.answer()

    context.chat_data["Date"] = get_date_string(query.data)

    query.message.edit_text(ASKFORIMAGE, reply_markup=img_search_markup)

    return state_image



def date_text(update: Update, context: CallbackContext) -> int:
    """
    Stores the date string (provided by the user), then asks the user for an image or search term

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        state_image (int): return to conversation handler and wait for an image or search term before executing the relevant method
    """

    context.chat_data["Date"] = update.message.text

    update.message.reply_text(ASKFORIMAGE, reply_markup=img_search_markup)
    return state_image



def img_search_term(update: Update, context: CallbackContext) -> int:
    """
    Stores the image search term (user provided), then asks the user which image provider to use

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        state_img_provider (int): return to conversation handler and wait for an image provider before executing the relevant method
    """

    context.chat_data["Image_Seed"] = update.message.text

    context.bot.delete_message(
        chat_id=update.effective_chat.id, message_id=update.message.message_id - 1
    )
    update.message.reply_text(ASKFORPROVIDER, reply_markup=provider_markup)

    return state_img_provider



def img_search_term_cb(update: Update, context: CallbackContext) -> int:
    """
    Stores the image search term (provided by on screen options), then asks the user which image provider to use

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        state_img_provider (int): return to conversation handler and wait for an image provider before executing the relevant method
    """

    query = update.callback_query
    query.answer()

    context.chat_data["Image_Seed"] = query.data

    query.message.edit_text(ASKFORPROVIDER, reply_markup=provider_markup)

    return state_img_provider



def change_background(update: Update, context: CallbackContext) -> int:
    """
    Calls the specified provider's genereation method to re-generate the image
    Sets a variable so the generation method knows not to update the provider

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        status (int): returns the status returned by the generation method
    """

    query = update.callback_query
    query.answer()

    context.chat_data["ChangeBG"] = True

    try:
        if context.chat_data["Provider"] == str(cbd_src_wallhaven):
            return wallhavenimage(update, context)
        elif context.chat_data["Provider"] == str(cbd_src_unsplash):
            return unsplashimage(update, context)
    except KeyError:
        query.message.reply_text("This image source will just provide the same image.\nTo change the image you will need to change the provider", reply_markup=InlineKeyboardMarkup(FinishMenuKeyboard))
        return state_done_menu



def wallhavenimage(update: Update, context: CallbackContext) -> int:
    """
    Uses the search term to get a maching image.
    The image, quote, source & optional date is submitted for generation of the final quote image.
    Sends the completed image to the user.
    Checks if quotes created in the chat should be saved. The image is saved if so.
    Finally prompt the user for the next action.

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        On successful generation:
            state_done_menu (int): return to conversation handler and wait for a completed menu option before executing the relevant method
        If no results are found:
            status (int): returns the status returned by the new_img_src method
        If a different error occurs:
            status (int): returns the status returned by the new_img_src method
    """

    query = update.callback_query
    query.answer()

    # Checks if this is a re-generation of an image, if so it won't update the image provider
    # If this isnt here, the provider will be set to whichever provider carries the same value as the "New BG" button
    if not context.chat_data["ChangeBG"]:
        context.chat_data["Provider"] = query.data
    else:
        context.chat_data["ChangeBG"] = False

    try:  # Try to get the image and map the quote
        wait_msg = query.message.reply_text(PLZ_WAIT_MSG)

        bg = wallhaven.get_random_image(context.chat_data["Image_Seed"])
        final_img = image_modify.draw_text_layer(
            bg,
            context.chat_data["Quote"],
            context.chat_data["Source"],
            context.chat_data["Date"],
        )

        query.message.reply_document(
            tele_img_convert(final_img), caption=FIRSTIMAGEQUOTE
        )
        context.bot.deleteMessage(
            message_id=wait_msg.message_id, chat_id=query.message.chat_id
        )

        context.chat_data["LocalStorageFilePath"] = local_storage.do_local_storage(
            update, context, final_img
        )

        query.message.reply_text(FINISHEDMESSAGE, reply_markup=finish_kb_markup)

        return state_done_menu
    except IndexError:  # Catch Index Error (caused by no results)
        print(
            f"Wallhaven scraper found no results for {context.chat_data['Image_Seed']}"
        )
        query.message.reply_text("No images with that seed, please send another seed")
        return new_img_src(update, context)
    except Exception as exc_txt:  # Catch anything else that might break
        print(exc_txt)
        query.message.reply_text("I'm sorry, Something went wrong")
        return new_img_src(update, context)



def bingimage(update: Update, context: CallbackContext) -> int:
    """
    Fetches the Bing image.
    The image, quote, source & optional date is submitted for generation of the final quote image.
    Sends the completed image to the user.
    Checks if quotes created in the chat should be saved. The image is saved if so.
    Finally prompt the user for the next action.

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        state_done_menu (int): return to conversation handler and wait for a completed menu option before executing the relevant method
    """

    query = update.callback_query
    query.answer()

    wait_msg = query.message.reply_text(PLZ_WAIT_MSG)

    bg = bing.get_image()
    final_img = image_modify.draw_text_layer(
        bg,
        context.chat_data["Quote"],
        context.chat_data["Source"],
        context.chat_data["Date"],
    )

    query.message.reply_document(tele_img_convert(final_img), caption=FIRSTIMAGEQUOTE)
    context.bot.deleteMessage(
        message_id=wait_msg.message_id, chat_id=query.message.chat_id
    )

    context.chat_data["LocalStorageFilePath"] = local_storage.do_local_storage(
        update, context, final_img
    )

    query.message.reply_text(FINISHEDMESSAGE, reply_markup=finish_kb_markup)

    return state_done_menu



def unsplashimage(update: Update, context: CallbackContext) -> int:
    """
    Uses the search term to get a maching image, artist information is included in the returned object.
    The image, quote, source & optional date is submitted for generation of the final quote image.
    Sends the completed image to the user, including the attribution info & links that is required by the unsplash API.
    Checks if quotes created in the chat should be saved. The image is saved if so.
    Finally prompt the user for the next action.

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        On successful generation:
            state_done_menu (int): return to conversation handler and wait for a completed menu option before executing the relevant method
        If no results are found:
            status (int): returns the status returned by the new_img_src method
        If a different error occurs:
            status (int): returns the status returned by the new_img_src method
    """

    query = update.callback_query
    query.answer()

    # Checks if this is a re-generation of an image, if so it won't update the image provider
    # If this isnt here, the provider will be set to whichever provider carries the same value as the "New BG" button
    if not context.chat_data["ChangeBG"]:
        context.chat_data["Provider"] = query.data
    else:
        context.chat_data["ChangeBG"] = False

    try:  # Try to get the image and map the quote
        wait_msg = query.message.reply_text(PLZ_WAIT_MSG)

        bg_tuple = unsplash.get_image(context.chat_data["Image_Seed"])
        final_img = image_modify.draw_text_layer(
            bg_tuple[2],
            context.chat_data["Quote"],
            context.chat_data["Source"],
            context.chat_data["Date"],
        )
        captiontext = "{0}\n\nImage by [{1}]({2}?utm_source={3}&utm_medium=referral) on [Unsplash](https://unsplash.com/?utm_source={3}&utm_medium=referral)".format(
            FIRSTIMAGEQUOTE,
            bg_tuple[0],
            bg_tuple[1],
            os.getenv("UnsplashAppName")
        )
        query.message.reply_document(
            tele_img_convert(final_img), caption=captiontext, parse_mode="MarkdownV2"
        )
        context.bot.deleteMessage(
            message_id=wait_msg.message_id, chat_id=query.message.chat_id
        )

        context.chat_data["LocalStorageFilePath"] = local_storage.do_local_storage(
            update, context, final_img
        )

        query.message.reply_text(FINISHEDMESSAGE, reply_markup=finish_kb_markup)

        return state_done_menu
    except IndexError:  # Catch Index Error (caused by no results)
        print( f"Unsplash scraper found no results for {context.chat_data['Image_Seed']}" )
        query.message.reply_text("No images with that seed, please send another seed")
        return new_img_src(update, context)
    except Exception as exc_txt:  # Catch anything else that might break
        print(exc_txt)
        query.message.reply_text("I'm sorry, Something went wrong")
        return new_img_src(update, context)



def uploadedimage(update: Update, context: CallbackContext) -> int:
    """
    Received the image from the user
    The image, quote, source & optional date is submitted for generation of the final quote image.
    Sends the completed image to the user.
    Checks if quotes created in the chat should be saved. The image is saved if so.
    Finally prompt the user for the next action.

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        state_done_menu (int): return to conversation handler and wait for a completed menu option before executing the relevant method
    """

    imagefile = context.bot.get_file(update.message.photo[-1].file_id)
    imagebytes = io.BytesIO(imagefile.download_as_bytearray())

    bg = Image.open(imagebytes)

    final_img = image_modify.draw_text_layer(
        bg,
        context.chat_data["Quote"],
        context.chat_data["Source"],
        context.chat_data["Date"],
    )
    update.message.reply_document(tele_img_convert(final_img), caption=FIRSTIMAGEQUOTE)

    context.chat_data["LocalStorageFilePath"] = local_storage.do_local_storage(
        update, context, final_img
    )

    update.message.reply_text(FINISHEDMESSAGE, reply_markup=finish_kb_markup)

    return state_done_menu



def new_img_src(update: Update, context: CallbackContext) -> int:
    """
    Prompt the user for an image or search term

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        state_image (int): return to conversation handler and wait for an image or search term before executing the relevant method
    """

    query = update.callback_query
    query.answer()

    query.message.reply_text(ASKFORIMAGE, reply_markup=img_search_markup)

    return state_image



def callback_cancel(update: Update, context: CallbackContext) -> int:
    """
    Fallback method to cancel & end the conversation

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        END (int): status update to end conversation
    """

    query = update.callback_query
    query.answer()

    context.chat_data.clear()

    query.message.edit_text(ENDCONVO + query.from_user.first_name)

    return ConversationHandler.END



def cancel(update: Update, context: CallbackContext) -> int:
    """
    Fallback method to cancel & end the conversation

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching

    Returns:
        END (int): status update to end conversation
    """

    context.chat_data.clear()

    update.message.reply_text(ENDCONVO + update.message.from_user.username)
    return ConversationHandler.END



def main():
    """
    Run the main conversation handler
    """
    # Create the Updater and pass it your bot's token.
    updater = Updater(os.getenv("TOKEN"))

    # Get the dispatcher to register handlers
    dispatcher = updater.dispatcher

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("cancel", cancel)],
        states={
            state_quote: [MessageHandler(Filters.text, quote)],
            state_source: [MessageHandler(Filters.text, source)],
            state_date_menu: [
                CallbackQueryHandler(date_selection),
                MessageHandler(Filters.text, date_text),
            ],
            state_image: [
                MessageHandler(Filters.text, img_search_term),
                MessageHandler(Filters.photo, uploadedimage),
                CallbackQueryHandler(bingimage, pattern="#BING#"),
                CallbackQueryHandler(img_search_term_cb),
            ],
            state_img_provider: [
                CallbackQueryHandler(
                    wallhavenimage, pattern="^" + str(cbd_src_wallhaven) + "$"
                ),
                CallbackQueryHandler(
                    unsplashimage, pattern="^" + str(cbd_src_unsplash) + "$"
                ),
            ],
            state_done_menu: [
                CallbackQueryHandler(again, pattern="^" + str(cbd_quote) + "$"),
                CallbackQueryHandler(
                    change_background, pattern="^" + str(cbd_change_image) + "$"
                ),
                CallbackQueryHandler(
                    new_img_src, pattern="^" + str(cbd_new_bg_src) + "$"
                ),
                CallbackQueryHandler(
                    callback_cancel, pattern="^" + str(cbd_done) + "$"
                ),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    dispatcher.add_handler(conv_handler)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()



if __name__ == "__main__":
    main()
