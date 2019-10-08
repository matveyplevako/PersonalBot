from services.logger import logger
from services.sport_attendance import attendance_utils
from telegram.ext import ConversationHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton
from services.initial.functions import menu
from datetime import datetime

ADD_START, ADD_FINISH, GET_FOR_PERIOD = range(3)


def select_option(update, context):
    bot = context.bot
    logger.info("Select option for attendance")
    keyboard = [
        [KeyboardButton("Add attendance")],
        [KeyboardButton("Get my attendance for this term"), KeyboardButton("Get my attendance for period")],
        [KeyboardButton("Back to menu")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    bot.send_message(update.message.chat_id, "Select an option",
                     reply_markup=reply_markup)


def add_record(update, context):
    bot = context.bot
    logger.info("Start process of adding new record to attendance")

    keyboard = [
        [KeyboardButton("Now")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)

    bot.send_message(update.message.chat_id, "enter the arrival time in format\noptional[M-D] h:m\nor /cancel",
                     reply_markup=reply_markup)
    return ADD_START


def add_start_time(update, context):
    bot = context.bot
    chat_data = context.chat_data
    date = update.message.text

    keyboard = [
        [KeyboardButton("Now")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)

    now = datetime.now()
    chat_data['month'] = now.month
    chat_data['day'] = now.day
    try:
        if date == "Now":
            date = str(datetime.now().replace(microsecond=0))
        elif len(date.split()) == 2:
            date = datetime.strptime(date, '%m-%d %H:%M').replace(year=now.year)
            chat_data['month'] = date.month
            chat_data['day'] = date.day
            date = str(date)
        else:
            date = str(datetime.strptime(date, '%H:%M').replace(year=now.year, month=now.month, day=now.day))
    except:
        bot.send_message(update.message.chat_id, "enter valid date and time and try again")
        return cancel(update, context)

    chat_data['start'] = date
    bot.send_message(update.message.chat_id, "enter the leaving time in format\nh:m", reply_markup=reply_markup)
    return ADD_FINISH


def add_finish_time(update, context):
    bot = context.bot
    chat_data = context.chat_data
    date = update.message.text
    now = datetime.now()
    try:
        if date == "Now":
            date = str(datetime.now().replace(microsecond=0))
        else:
            date = str(
                datetime.strptime(date, '%H:%M').replace(year=now.year, month=chat_data['month'], day=chat_data['day']))
    except Exception as e:
        logger.error(e)
        bot.send_message(update.message.chat_id, "enter valid date and time and try again")
        return cancel(update, context)

    attendance_utils.add_attendance(str(update.message.chat_id), chat_data['start'], date)
    bot.send_message(update.message.chat_id, "saved")
    menu(update, context)
    return ConversationHandler.END


def request_period_from_user(update, context):
    bot = context.bot
    bot.send_message(update.message.chat_id, "Enter period\nOptional[Y-]M-D:Optional[Y-]M-D\nor /cancel")
    return GET_FOR_PERIOD


def get_attendance_for_period(update, context):
    bot = context.bot
    try:
        start, finish = update.message.text.split(":")
        now = datetime.now()
        if len(start.split("-")) == 3 and len(finish.split("-")) == 3:
            start = str(datetime.strptime(start, '%Y-%m-%d'))
            finish = str(datetime.strptime(finish, '%Y-%m-%d'))
        else:
            start = str(datetime.strptime(start, '%m-%d').replace(year=now.year))
            finish = str(datetime.strptime(finish, '%m-%d').replace(year=now.year))
    except Exception as e:
        logger.error(e)
        bot.send_message(update.message.chat_id, "enter valid date and time and try again")
        return cancel(update, context)

    hours, minutes = attendance_utils.get_attendance_for_period(update.message.chat_id, start, finish)
    bot.send_message(update.message.chat_id, f"Your attendance:\n{hours} hours {minutes} minutes")
    menu(update, context)
    return ConversationHandler.END


def get_attendance_for_this_term(update, context):
    bot = context.bot
    hours, minutes = attendance_utils.get_attendance_for_this_term(update.message.chat_id)
    bot.send_message(update.message.chat_id, f"Your attendance:\n{hours} hours {minutes} minutes")
    menu(update, context)


def cancel(update, context):
    bot = context.bot
    logger.error("Cancel the process")
    menu(update, context)
    return ConversationHandler.END
