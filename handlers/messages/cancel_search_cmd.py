from telebot.types import Message
from keyboards.inline_keyboard.start import start_inline_keyboard
from loader import bot
from config_data.config import BOT_COMMANDS
from .utils.state_data import StateData


@bot.message_handler(state="*", commands=[BOT_COMMANDS[1][0]])  # /cancel_search
def cancel_command_state(message: Message) -> None:
    """
    Catching any text message from user contains bot command "cancel_search"
    and canceling current user state(reply_msg_cancel_search)

    :param message: user reply data
    :type message: Message
    """

    reply_msg_cancel_search(message.chat.id, message.from_user.id)


@bot.message_handler(state="*", regexp=BOT_COMMANDS[1][1])  # 'cancel_search' shortcut
def cancel_shortcut_state(message: Message) -> None:
    """
    Catching any text message from user contains bot command shortcut
    "cancel_search" and canceling current user state(reply_msg_cancel_search)

    :param message: user reply data
    :type message: Message
    """

    reply_msg_cancel_search(message.chat.id, message.from_user.id)


def reply_msg_cancel_search(chat_id: int, user_id) -> None:
    """
    Canceling current user state and sending appropriate message to
    user.

    :param chat_id: Chat identifier
    :type chat_id: int
    :param user_id: User identifier
    :type user_id: int
    """

    text = 'Your search state was canceled.'
    StateData.delete_state(chat_id, user_id)
    bot.send_message(chat_id=chat_id,
                     text=text,
                     reply_markup=start_inline_keyboard
                     )
