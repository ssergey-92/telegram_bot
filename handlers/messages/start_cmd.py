from telebot.types import Message

from keyboards.inline_keyboard.start import start_inline_keyboard
from loader import bot
from .utils.state_data import StateData


@bot.message_handler(commands=["start"])
def start_command(message: Message) -> None:
    reply_msg_start(message.chat.id, message.from_user.id,
                    message.from_user.full_name)


def reply_msg_start(chat_id: int, user_id: int, user_name: str) -> None:
    StateData.delete_state(chat_id, user_id)
    text = ("Welcome, {name}!\nI'm Hotel Dataprovider Bot from Too "
            "Easy Travel Agency.\nI can help you to find a suitable hotel.").format(
        name=user_name
    )
    bot.send_message(chat_id=chat_id,
                     text=text,
                     reply_markup=start_inline_keyboard
                     )
