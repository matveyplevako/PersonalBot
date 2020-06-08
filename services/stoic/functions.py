from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ParseMode
from telegram.ext import ConversationHandler
from services.DataBase import DB
import datetime
import json
import logging
import requests
from os import environ

PROCESS_DATA = 0

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)


def stoic_menu(update, context):
    bot = context.bot
    keyboard = [
        [KeyboardButton("Get quote for today")],
        [KeyboardButton("Manage subscription")],
        [KeyboardButton("Get quote by day")],
        [KeyboardButton("Back to menu")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    bot.send_message(update.message.chat_id, "Select an option",
                     reply_markup=reply_markup)


def stoic_subscription_menu(update, context):
    bot = context.bot
    keyboard = [
        [KeyboardButton("Set receiving hour")],
        [KeyboardButton("Set quotes day")],
        [KeyboardButton("Cancel daily subscription")],
        [KeyboardButton("Daily stoic quote menu")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    bot.send_message(update.message.chat_id, "Select an option",
                     reply_markup=reply_markup)


def get_data_from_user(text):
    def func(update, context):
        bot = context.bot
        bot.send_message(update.message.chat_id, f"{text}")
        return PROCESS_DATA

    return func


def get_quote_for_today(update, context):
    stoic_info = get_stoic_db()
    res = stoic_info.get_items(user_id=update.message.chat_id)
    day = 0
    if len(res) != 0:
        start_day = res[0][1]
        when_added = res[0][3]
        day = (int(start_day) + delta(*list(map(int, when_added.split("-"))))) % 366

    get_quote_selected_day(update, context, day)


def get_quote_selected_day(update, context, day=None):
    bot = context.bot
    if day is None:
        try:
            day = int(update.message.text)
            assert 0 <= day <= 365
        except:
            bot.send_message(update.message.chat_id, "select day in range [0, 365]")
            stoic_menu(update, context)
            return ConversationHandler.END

    day = str(day)

    keyboard = [

        [InlineKeyboardButton("🇬🇧 original", callback_data=f'eng {day}')]
    ]
    keyboard[0].insert(0, InlineKeyboardButton("🇷🇺 translate", callback_data=f'ru {day}'))
    reply_markup = InlineKeyboardMarkup(keyboard)
    with open("services/stoic/data/img.json") as images:
        image = json.load(images)[day]
    bot.send_message(update.message.chat_id, f"[​​​​​​​​​​​]({image}) Day {int(day)}.", reply_markup=reply_markup,
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
    if chosen == "ru":
        keyboard[0].pop(0)
    if chosen == "eng":
        keyboard[0].pop(-2)
    if chosen == "img":
        keyboard[0].pop(-1)

    reply_markup = InlineKeyboardMarkup(keyboard)

    if chosen == "img":
        with open(f"services/stoic/data/{chosen}.json") as data:
            content = f"[​​​​​​​​​​​]({json.load(data)[day]}) Day {int(day)}."
    else:
        if int(day) > 230 and chosen == "ru":
            with open(f"services/stoic/data/eng.json") as data:
                content = translate(json.load(data)[day])
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


# Add 3 hours to get msk time
def set_receiving_time(update, context):
    bot = context.bot

    try:
        time = update.message.text
        hour, minute = map(int, time.split(":"))
        assert 0 <= hour <= 23
        assert 0 <= minute <= 59
    except:
        bot.send_message(update.message.chat_id, "select hour and minute in range [0, 23], [0, 59]")
        stoic_menu(update, context)
        return ConversationHandler.END

    bot.send_message(update.message.chat_id, f"Updating...")
    stoic_menu(update, context)

    stoic_info = get_stoic_db()
    res = stoic_info.get_items(user_id=update.message.chat_id)
    start_day = "0"
    when_added = datetime.datetime.now().strftime('%Y-%m-%d')

    if len(res) != 0:
        stoic_info.delete_item(user_id=update.message.chat_id)
        start_day = res[0][1]
        when_added = res[0][3]
        delete_job(update, context)

    create_job(update, context, time)
    stoic_info.add_item(user_id=update.message.chat_id, start_day=start_day, time=time, when_added=when_added)

    day = (int(start_day) + delta(*list(map(int, when_added.split("-"))))) % 366
    bot.send_message(update.message.chat_id, f"You will now receive new quotes from {day} day at {time}")

    return ConversationHandler.END


def set_day(update, context):
    bot = context.bot

    try:
        day = int(update.message.text)
        assert 0 <= day <= 365
        day = str(day)
    except:
        bot.send_message(update.message.chat_id, "select day in range [0, 365]")
        stoic_menu(update, context)
        return ConversationHandler.END

    bot.send_message(update.message.chat_id, f"Updating...")
    stoic_menu(update, context)

    stoic_info = get_stoic_db()
    res = stoic_info.get_items(user_id=update.message.chat_id)
    time = "12:00"
    when_added = datetime.datetime.now().strftime('%Y-%m-%d')
    if len(res) != 0:
        stoic_info.delete_item(user_id=update.message.chat_id)
        time = res[0][2]
        delete_job(update, context)

    create_job(update, context, time)
    stoic_info.add_item(user_id=update.message.chat_id, start_day=day, time=time, when_added=when_added)

    day = (int(day) + delta(*list(map(int, when_added.split("-"))))) % 366
    bot.send_message(update.message.chat_id, f"You will now receive new quotes from {day} day at {time}")

    return ConversationHandler.END


def log_jobs(job_queue):
    for job in job_queue:
        LOGGER.info(f"{job.name, job.interval_seconds, job.removed, job.interval}")


def delete_job(update, context):
    job_queue = context.job_queue
    chat_id = str(update.message.chat_id)
    LOGGER.info("deleting previous job")
    jobs = job_queue.get_jobs_by_name(chat_id)
    LOGGER.info("was:")
    log_jobs(context.job_queue.get_jobs_by_name(chat_id))
    for job in jobs:
        if not job.removed:
            job.schedule_removal()
    LOGGER.info("now:")
    log_jobs(context.job_queue.get_jobs_by_name(chat_id))


def create_job(update, context, time):
    job_queue = context.job_queue
    chat_id = str(update.message.chat_id)
    LOGGER.info("creating new job")
    LOGGER.info("was:")
    log_jobs(job_queue.get_jobs_by_name(chat_id))
    hour, minute = map(int, time.split(":"))
    if int(hour) > 2:
        running_time = datetime.time(hour=(int(hour) - 3), minute=minute)
    else:
        running_time = datetime.time(hour=21 + int(hour), minute=minute)

    job_queue.run_daily(daily_job, time=running_time, context={"chat_id": chat_id}, name=chat_id)
    LOGGER.info("now:")
    log_jobs(job_queue.get_jobs_by_name(chat_id))


def stop_receiving_quotes(update, context):
    bot = context.bot
    delete_job(update, context)
    bot.send_message(update.message.chat_id, "subscription stopped")
    stoic_menu(update, context)

    stoic_info = get_stoic_db()
    res = stoic_info.get_items(user_id=update.message.chat_id)
    if len(res) != 0:
        delete_job(update, context)
        stoic_info.delete_item(user_id=update.message.chat_id)


def get_stoic_db():
    return DB("stoic_info", user_id="TEXT", start_day="TEXT", time="TEXT", when_added="TEXT")


def delta(year, month, day):
    now = datetime.datetime.now()
    start_of_the_year = datetime.datetime(year=year, month=month, day=day)
    return (now - start_of_the_year).days


def daily_job(context):
    bot = context.bot
    job = context.job
    chat_id = str(job.context['chat_id'])
    stoic_db = get_stoic_db()
    res = stoic_db.get_items(user_id=chat_id)
    if len(res) == 0:
        return

    start_day = res[0][1]
    when_added = res[0][3]
    day = (int(start_day) + delta(*list(map(int, when_added.split("-"))))) % 366

    keyboard = [
        [InlineKeyboardButton("🇬🇧 original", callback_data=f'eng {day}')]
    ]
    keyboard[0].insert(0, InlineKeyboardButton("🇷🇺 translate", callback_data=f'ru {day}'))
    reply_markup = InlineKeyboardMarkup(keyboard)
    with open("services/stoic/data/img.json") as images:
        image = json.load(images)[str(day)]
    bot.send_message(chat_id, f"[​​​​​​​​​​​]({image})Daily quote❕\nDay {int(day)}.", reply_markup=reply_markup,
                     parse_mode=ParseMode.MARKDOWN)


def cancel(update, context):
    stoic_menu(update, context)
    return ConversationHandler.END


def translate(my_text):
    params = {
        "key": environ["TRANSLATE_KEY"],
        "text": my_text,
        "lang": 'en-ru'
    }
    response = requests.get("https://translate.yandex.net/api/v1.5/tr.json/translate", params=params)
    return response.json()['text'][0]
