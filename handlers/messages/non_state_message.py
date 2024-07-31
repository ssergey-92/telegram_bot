from telebot.types import Message

from keyboards.inline.start import start_inline_keyboard
from loader import bot
from project_logging.bot_logger import bot_logger

accepted_welcome_msg = ("hi", "hello", "hello-world", "Привет")
success_reply_msg = "Hi, {name}!\nNow is the best time to select a hotel."
reply_msg_for_unrecognised = (
    "'{received_msg}' is not recognised.\nSelect one of below options:"
)


@bot.message_handler()
def non_state_text_message(message: Message) -> None:
    """ Catch unstated incoming user message.

    Compare message text with possible welcome message and send appropriate
    reply.

    :param message: user reply data
    :type message: Message

    """
    bot_logger.info(
        f"{message.text=}, {message.chat.id=},{message.from_user.id=}"
    )
    if message.text.lower().strip() in accepted_welcome_msg:
        reply_msg = success_reply_msg.format(name=message.from_user.full_name)
    else:
        reply_msg = reply_msg_for_unrecognised.format(
            received_msg=message.text,
        )
    bot_logger.debug(
        f"{reply_msg=}, {message.chat.id=}, {message.from_user.id=}",
    )
    bot.send_message(
        message.chat.id, reply_msg, reply_markup=start_inline_keyboard,
    )
