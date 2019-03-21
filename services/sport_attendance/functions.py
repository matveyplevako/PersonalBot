from services.logger import logger
from services.sport_attendance import attendance_utils
from telegram.ext import ConversationHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup
from services.initial.functions import menu
from datetime import datetime

ADD_START, ADD_FINISH = range(2)


def select_option(bot, update):
    logger.info("Select option for attendance")
    keyboard = [
        [KeyboardButton("Add attendance")],
        [KeyboardButton("Get my attendance for this term")],
        [KeyboardButton("Back to menu")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    bot.send_message(update.message.chat_id, "Select an option",
                     reply_markup=reply_markup)


def add_record(bot, update):
    logger.info("Start process of adding new record to attendance")
    bot.send_message(update.message.chat_id, "enter the arrival time in format\noptional[M-D] h:m\nor /cancel")
    return ADD_START


def add_start_time(bot, update, chat_data):
    date = update.message.text
    now = datetime.now()
    try:
        if len(date.split()) == 2:
            date = str(datetime.strptime(date, '%m-%d %H:%M').replace(year=now.year))
        else:
            date = str(datetime.strptime(date, '%H:%M').replace(year=now.year, month=now.month, day=now.day))
    except:
        bot.send_message(update.message.chat_id, "enter valid date and time")
        return cancel(bot, update)

    chat_data['start'] = date
    bot.send_message(update.message.chat_id, "enter the leaving time in format\nhh:mm")
    return ADD_FINISH


def add_finish_time(bot, update, chat_data):
    date = update.message.text
    now = datetime.now()
    try:
        date = str(datetime.strptime(date, '%H:%M').replace(year=now.year, month=now.month, day=now.day))
    except:
        bot.send_message(update.message.chat_id, "enter valid date and time")
        return cancel(bot, update)

    attendance_utils.add_attendance(str(update.message.chat_id), chat_data['start'], date)
    bot.send_message(update.message.chat_id, "saved")
    menu(bot, update)


def cancel(bot, update):
    logger.error("Cancel the process")
    menu(bot, update)
    return ConversationHandler.END
