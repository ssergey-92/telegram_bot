from telebot.types import Message
from keyboards.inline_keyboard.start import start_inline_keyboard
from loader import bot
from config_data.config import BOT_COMMANDS
from .top_budget_hotels_state import reply_msg_low_price

low_price_shortcut = BOT_COMMANDS[3][1]
high_price_shortcut = BOT_COMMANDS[4][1]
best_deal_shortcut = BOT_COMMANDS[5][1]
history_shortcut = BOT_COMMANDS[6][1]


@bot.message_handler()
def non_state_text_message(message: Message) -> None:
    if message.text == low_price_shortcut:
        reply_msg_low_price(message.chat.id, message.from_user.id)
        return None
    elif message.text == high_price_shortcut:
        return None
    elif message.text == best_deal_shortcut:
        return None
    elif message.text == history_shortcut:
        return None
    elif message.text.lower().strip() in ('hi', 'hello', 'hello-world', 'Привет'):
        text = 'Hi, {name}!\nNow is the best time to select a hotel.'.format(
            name=message.from_user.full_name
        )
    else:
        text = (" '{received_text}' is not recognised.\nSelect one of below "
                "options").format(
            received_text=message.text
        )
    bot.send_message(
        chat_id=message.chat.id,
        text=text,
        reply_markup=start_inline_keyboard
    )


