from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler
from services.initial.functions import menu
import datetime
import json

PROCESS_DAY = 0


def stoic_menu(update, context):
    bot = context.bot
    keyboard = [
        [KeyboardButton("Get quote for today")],
        [KeyboardButton("Set the hour to receive new quote")],
        [KeyboardButton("Get quote by day")],
        [KeyboardButton("Back to menu")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    bot.send_message(update.message.chat_id, "Select an option",
                     reply_markup=reply_markup)


def get_day_from_user(update, context):
    bot = context.bot

    bot.send_message(update.message.chat_id, "Send the day you want to get quote for\nor /cancel")
    return PROCESS_DAY


def get_quote_for_today(update, context):
    now = datetime.datetime.now()
    current_year = datetime.datetime.now().year
    start_of_the_year = datetime.datetime(year=current_year, day=1, month=1)
    delta = (now - start_of_the_year).days

    get_quote_selected_day(update, context, delta)


def get_quote_selected_day(update, context, day=None):
    bot = context.bot
    if day is None:
        try:
            day = int(update.message.text)
            assert 1 <= day <= 366
        except:
            bot.send_message(update.message.chat_id, "select day in range [1, 366]")
            menu(update, context)
            return ConversationHandler.END

    day = str(day)

    keyboard = [

        [InlineKeyboardButton("🇬🇧 original", callback_data=f'eng {day}')]
    ]
    if int(day) <= 230:
        keyboard[0].insert(0, InlineKeyboardButton("🇷🇺 translate", callback_data=f'ru {day}'))
    reply_markup = InlineKeyboardMarkup(keyboard)
    with open("services/stoic/data/img.json") as images:
        image = json.load(images)[day]
    bot.send_message(update.message.chat_id, f"[​​​​​​​​​​​]({image}) Day {day}.", reply_markup=reply_markup,
                     parse_mode=ParseMode.MARKDOWN)
    return ConversationHandler.END


def get_content(update, context):
    bot = context.bot
    query = update.callback_query
    query_data = query.data.split()
    chosen, day = query_data

    keyboard = [
        [InlineKeyboardButton("🇷🇺 translate", callback_data=f'ru {day}'),
         InlineKeyboardButton("🇬🇧 original", callback_data=f'eng {day}'),
         InlineKeyboardButton("📸 screen from book", callback_data=f'img {day}')]
    ]
    if chosen == "ru" or int(day) > 230:
        keyboard[0].pop(0)
    if chosen == "eng":
        keyboard[0].pop(1)
    if chosen == "img":
        keyboard[0].pop(2)

    reply_markup = InlineKeyboardMarkup(keyboard)

    if chosen == "img":
        with open(f"services/stoic/data/{chosen}.json") as data:
            content = f"[​​​​​​​​​​​]({json.load(data)[day]}) Day {day}."
    else:
        with open(f"services/stoic/data/{chosen}.json") as data:
            content = json.load(data)[day]

    bot.edit_message_text(
        chat_id=query.message.chat_id,
        message_id=query.message.message_id,
        text=content,
        reply_markup=reply_markup,
        parse_mode=ParseMode.MARKDOWN if chosen == "img" else None
    )


def cancel(update, context):
    menu(update, context)
    return ConversationHandler.END
