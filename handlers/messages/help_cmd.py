from telebot.types import Message

from keyboards.reply_keyboard.help import help_reply_keyboard
from loader import bot
from config_data.config import BOT_COMMANDS
from .utils.state_data import StateData

@bot.message_handler(commands=["help"])
def help_command(message: Message) -> None:
    reply_msg_help(message.chat.id, message.from_user.id)


def create_help_text() -> str:
    text = ("Kindly familiarize yourself with following commands:\n"
            "Command - Shortcut - Description\n")
    for commands in BOT_COMMANDS:
        text = ''.join([text,
                        f"/{commands[0]} - {commands[1]} - {commands[2]}\n"])
    return text


def reply_msg_help(chat_id: int, user_id: int) -> None:
    StateData.delete_state(chat_id, user_id)
    bot.send_message(chat_id=chat_id,
                     text=help_text,
                     reply_markup=help_reply_keyboard
                     )


help_text = create_help_text()


