from telebot.types import Message

from loader import bot
from states.history import HistoryStates
from config_data.config import BOT_COMMANDS
from .utils.history_state_meseges import HandleHistoryMsg

history_cmd = BOT_COMMANDS[6][0]


@bot.message_handler(commands=[history_cmd])
def history_command(message: Message) -> None:
    """
    Catching unstated incoming user reply message which contains bot
    command "history" and calling function(reply_msg_history()) for
    handling command.

    :param message: user reply data
    :type message: Message
    """

    reply_msg_history(message.chat.id, message.from_user.id)


def reply_msg_history(chat_id: int, user_id: int) -> None:
    """
    Intermediate function for calling HandleHistoryMsg.initialize_command()
    due to different types of user reply formats (Message, Callback)

    :param chat_id: Chat identifier
    :type chat_id: int
    :param user_id: User identifier
    :type user_id: int
    """

    HandleHistoryMsg.initialize_command(chat_id, user_id)


@bot.message_handler(state=HistoryStates.records_number)
def records_number_state(message: Message) -> None:
    """
    Catching state: HistoryStates.records_number and calling
    HandleHistoryMsg.records_number() for handling it.

    :param message: user reply data
    :type message: Message
    """

    HandleHistoryMsg.records_number(message.chat.id, message.from_user.id,
                                    message.text)
