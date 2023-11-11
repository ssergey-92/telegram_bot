from telebot.types import Message

from keyboards.inline_keyboard.start import start_inline_keyboard
from loader import bot
from config_data.config import BOT_COMMANDS
from .utils.state_data import StateData

start_cmd = BOT_COMMANDS[0][0]


@bot.message_handler(commands=[start_cmd])
def start_command(message: Message) -> None:
    """
    Catching unstated incoming user reply message which contains bot
    command "start" and calling function( reply_msg_start()) for
    handling command.

    :param message: user reply data
    :type message: Message
    """

    reply_msg_start(message.chat.id, message.from_user.id,
                    message.from_user.full_name)


def reply_msg_start(chat_id: int, user_id: int, user_name: str) -> None:
    """
    Deleting user hotel search state if exists and sending reply message with
    start text and start inline keyboard.

    :param chat_id: Chat identifier
    :type chat_id: int
    :param user_id: User identifier
    :type user_id: int
    :param user_name: Username
    :type user_name: str
    """

    StateData.delete_state(chat_id, user_id)
    text = ("Welcome, {name}!\nI'm Hotel Dataprovider Bot from Too "
            "Easy Travel Agency.\nI can help you to find a suitable hotel.").format(
        name=user_name
    )
    bot.send_message(chat_id=chat_id,
                     text=text,
                     reply_markup=start_inline_keyboard
                     )
