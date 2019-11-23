from telegram import ReplyKeyboardMarkup, KeyboardButton, ParseMode
import traceback
import sys
from telegram.utils.helpers import mention_html
import os


def menu(update, context):
    bot = context.bot
    keyboard = [
        [KeyboardButton("Daily stoic quote menu")],
        [KeyboardButton("Sport complex attendance")],
        [KeyboardButton("Settings")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=False,
                                       resize_keyboard=True)

    bot.send_message(update.message.chat_id, "Select an option", reply_markup=reply_markup)


def error_callback(update, context):
    devs = [os.environ["DEV_CHANNEL"]]
    trace = "".join(traceback.format_tb(sys.exc_info()[2]))
    payload = ""
    if update.effective_user:
        payload += f' with the user {mention_html(update.effective_user.id, update.effective_user.first_name)}'
    if update.effective_chat:
        payload += f' within the chat <i>{update.effective_chat.title}</i>'
        if update.effective_chat.username:
            payload += f' (@{update.effective_chat.username})'
    if update.poll:
        payload += f' with the poll id {update.poll.id}.'
    text = f"Hey.\n The error <code>{context.error}</code> happened{payload}. The full traceback:\n\n<code>{trace}" \
           f"</code>"
    for dev_id in devs:
        context.bot.send_message(dev_id, text, parse_mode=ParseMode.HTML)
    raise


def start(update, context):
    bot = context.bot
    keyboard = [
        [KeyboardButton("Menu")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=False,
                                       resize_keyboard=True)
    bot.send_message(update.message.chat_id, "Hello!", reply_markup=reply_markup)


def settings(update, context):
    bot = context.bot

    keyboard = [
        [KeyboardButton("Configure email receiver")],
        [KeyboardButton("Back to menu")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=False,
                                       resize_keyboard=True)

    bot.send_message(update.message.chat_id, "Select an option", reply_markup=reply_markup)
