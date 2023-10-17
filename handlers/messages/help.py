from telebot.types import Message, InputMediaPhoto
from keyboards.reply_keyboard.help import help_reply_keyboard
from loader import bot
from config_data.config import BOT_COMMANDS

data_info = [{'name': 'Fabulous Village', 'property_id': '4163290',
              'distance': '9.73 MILE', 'price_per_day': '79.88 USD',
              'price_per_stay': '$273 including all taxes', 'site_url': 'not exist',
              'hotel_address': 'Via Di Malafede 225, Rome, RM, 00125',
              'hotel_rating': 'not rated',
              'photos_url': [
                  'https://images.trvl-media.com/lodging/5000000/4170000/4163300/4163290/6f28937c.jpg?impolicy=resizecrop&rw=500&ra=fit',
                  'https://images.trvl-media.com/lodging/5000000/4170000/4163300/4163290/611e6963.jpg?impolicy=resizecrop&rw=500&ra=fit',
                  'https://images.trvl-media.com/lodging/5000000/4170000/4163300/4163290/46a0ba63.jpg?impolicy=resizecrop&rw=500&ra=fit',
                  'https://images.trvl-media.com/lodging/5000000/4170000/4163300/4163290/0165e7ed.jpg?impolicy=resizecrop&rw=500&ra=fit',
                  'https://images.trvl-media.com/lodging/5000000/4170000/4163300/4163290/e3dbc167.jpg?impolicy=resizecrop&rw=500&ra=fit']}]


@bot.message_handler(commands=["help"])
def help_command(message: Message) -> None:
    reply_msg_help(message.chat.id)


def create_help_text() -> str:
    text = ("Kindly familiarize yourself with following commands:\n"
            "Command - Shortcut - Description\n")
    for commands in BOT_COMMANDS:
        text = ''.join([text,
                        f"/{commands[0]} - {commands[1]} - {commands[2]}\n"])
    return text


def reply_msg_help(chat_id: int) -> None:
    bot.send_message(chat_id=chat_id,
                     text=help_text,
                     reply_markup=help_reply_keyboard
                     )


help_text = create_help_text()


