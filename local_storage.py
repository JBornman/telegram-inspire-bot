import os
import json
from datetime import datetime



def get_user_id_field(from_user):
    """
        Returns the term that will uniquely identify the user in an easily readible format.
        A username will be used if its set.
        If no username is set, The first name & Chat ID will be used
        
        Args:
            from_user (Update): from_message attribute of the the callback_query attribute or of the message attribute (non-callback)

        Return:
            User Identifier (str): Term that can be used to uniquely identify the user
    """

    if from_user.username:
        return from_user.username

    return f"{from_user.first_name}-{from_user.id}"



def evaluation(update):
    """
    Checks if the Chat ID (of the user or group) is in the list of chats where quotes should be saved

    Args:
        update (Update): incomming update object

    Returns:
        If in save list:
            File path (str): Returns the full path of the file to be saved
        If not in save list:
            False (bool): Return false to indicate quote should not be saved
    """

    chat_list = json.loads( os.getenv("LSChatList") )

    try:
        if str(update.callback_query.message.chat_id) in chat_list:
            return generate_file_path(update.callback_query.message, update.callback_query.from_user)
    except Exception:
        if str(update.message.chat_id) in chat_list:
            return generate_file_path(update.message, update.message.from_user)

    return False



#region File path Generators



def pvt_chat_filename(from_user):
    """
    Generates the file path for the quotes created in a private chat (DM the bot)

    Args:
        update (Update): incomming update object

    Returns:
        File path (str): Returns the full path of the file to be saved
    """

    filename = "{}-{}.png".format(get_user_id_field(from_user), datetime.strftime(datetime.now(), "%-d%-m%y%H%M%S"))
    path = os.path.join("Export", "Private", filename)
    return path



def group_chat_filename(message, from_user):
    """
    Generates the file path for the quotes created in a group chat

    Args:
        message (Update): message attribute of the incomming update object

    Returns:
        File path (str): Returns the full path of the file to be saved
    """

    group_name = message.chat.title
    user_id_field = get_user_id_field(from_user)
    timestamp = datetime.strftime( datetime.now(), "%-d%-m%y%H%M%S" )

    filename = f"{user_id_field}-{timestamp}.png"

    if os.getenv('LSGroupUserSubfolders'):
        path = os.path.join("Export", group_name, user_id_field, filename)
    else:
        path = os.path.join("Export", group_name, filename)

    return path



def generate_file_path(message, from_user):
    """
    Selector method that calls the correct file name generator method based on the group chat type

    Args:
        message (Update): message attribute of the incomming update object

    Returns:
        File path (str): Returns the full path of the file to be saved
    """

    if message.chat.type == "private":
        return pvt_chat_filename(from_user)

    return group_chat_filename(message, from_user)



#endregion



def save_image(image, path):
    """
    Saves the provided image to the specified location

    Args:
        image (PIL image): The completed quote image that is to be saved
        path (str): The file path on the file system where the image should be saved
    """

    folders = os.path.split(path)[0]

    if not os.path.exists(folders):
        os.makedirs(folders)

    image.save(path)



def do_local_storage(update, context, finalimg):
    """
    Checks if the path has been set. If not, this will check if the chat id (provided by update) is in the save list
    It then checks if the image should be saved, and if so, saves the image to the path.

    Args:
        update (Update): incomming update object
        context (CallbackContext): callback for dispatching
        finalimg (PIL image): The completed quote image that is to be saved

    Returns:
        context (CallbackContext): If the file path is set during execution, an updated version of the context with the file path specified will be returned.
        This ensures that the context is kept up to date and no additional processing or resaving context is done unless necessary
    """

    if not context.chat_data.get("LocalStorageFilePath"):
        context.chat_data["LocalStorageFilePath"] = evaluation(update)

    if context.chat_data.get("LocalStorageFilePath"):
        save_image(finalimg, context.chat_data["LocalStorageFilePath"])

    return context.chat_data["LocalStorageFilePath"]
