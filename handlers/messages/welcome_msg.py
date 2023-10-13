from telebot.types import Message
from keyboards.inline_keyboard.start import start_inline_keyboard
from loader import bot
from config_data.config import BOT_COMMANDS
from . import top_budget_hotels

################CHANGE MODULE
@bot.message_handler()
def welcome_message(message: Message):
    #change function
    text = "need to type"
    if message.text == BOT_COMMANDS[3][1]:
        top_budget_hotels.low_price_command(message=message)
    elif message.text.lower().strip() in ('hi', 'hello', 'hello-world', 'Привет'):
        text = 'Hi, {name}!\nNow is the best time to select a hotel.'.format(
            name=message.from_user.full_name
        )
    else:
        text = (" '{rcvd_text}' is not recognised.\nSelect one of below "
                "options").format(
            rcvd_text=message.text
        )
    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=start_inline_keyboard
    )


