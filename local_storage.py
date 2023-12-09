import os
import json
from datetime import datetime



async def get_user_id_field(update):
    """
        Returns the term that will uniquely identify the user in an easily readible format.
        A username will be used if its set.
        If no username is set, The first name & Chat ID will be used
        
        Args:
            update (Update): incomming update object

        Return:
            User Identifier (str): Term that can be used to uniquely identify the user
    """

    if update.from_user.username:
        return update.from_user.username

    return f"{update.from_user.first_name}-{update.from_user.id}"



async def evaluation(update):
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

    if str(update.message.chat.id) in chat_list:
        return await generate_file_path(update)
    else:
        return False



#region File path Generators



async def pvt_chat_filename(update):
    """
    Generates the file path for the quotes created in a private chat (DM the bot)

    Args:
        update (Update): incomming update object

    Returns:
        File path (str): Returns the full path of the file to be saved
    """

    filename = "{}-{}.png".format(await get_user_id_field(update), datetime.strftime(datetime.now(), "%-d%-m%y%H%M%S"))
    path = os.path.join("Export", "Private", filename)
    return path



async def group_chat_filename(update):
    """
    Generates the file path for the quotes created in a group chat

    Args:
        update (Update): incomming update object

    Returns:
        File path (str): Returns the full path of the file to be saved
    """

    group_name = update.message.chat.title
    user_id_field = await get_user_id_field(update)
    timestamp = datetime.strftime( datetime.now(), "%-d%-m%y%H%M%S" )

    filename = f"{user_id_field}-{timestamp}.png"

    if os.getenv('LSGroupUserSubfolders'):
        path = os.path.join("Export", group_name, user_id_field, filename)
    else:
        path = os.path.join("Export", group_name, filename)

    return path



async def generate_file_path(update):
    """
    Selector method that calls the correct file name generator method based on the group chat type

    Args:
        update (Update): incomming update object

    Returns:
        File path (str): Returns the full path of the file to be saved
    """

    if update.message.chat.type == "private":
        return await pvt_chat_filename(update)
    else:
        return await group_chat_filename(update)



#endregion



async def save_image(image, path):
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



async def do_local_storage(update, context, finalimg):
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
        context.chat_data["LocalStorageFilePath"] = await evaluation(update)

    if context.chat_data.get("LocalStorageFilePath"):
        await save_image(finalimg, context.chat_data["LocalStorageFilePath"])

    return context.chat_data.get("LocalStorageFilePath")
