from telegram.ext import ConversationHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton
from services.logger import logger


def menu(update, context):
    bot = context.bot
    logger.info("Menu command")
    keyboard = [
        [KeyboardButton("Sport complex attendance")],
        [KeyboardButton("Settings")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=False,
                                       resize_keyboard=True)

    bot.send_message(update.message.chat_id, "Select an option", reply_markup=reply_markup)


def start(update, context):
    bot = context.bot
    logger.info("Start command")
    keyboard = [
        [KeyboardButton("Menu")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=False,
                                       resize_keyboard=True)
    bot.send_message(update.message.chat_id, "Hello!", reply_markup=reply_markup)


def settings(update, context):
    bot = context.bot
    logger.info("Settings command")

    keyboard = [
        [KeyboardButton("Configure email receiver")],
        [KeyboardButton("Back to menu")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=False,
                                       resize_keyboard=True)

    bot.send_message(update.message.chat_id, "Select an option", reply_markup=reply_markup)
