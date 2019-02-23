from telegram.ext import Updater
from telegram.bot import Bot
from telegram.ext import CommandHandler
from telegram.ext import MessageHandler, RegexHandler
from telegram.ext import ConversationHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton, ParseMode
from telegram.ext import Filters
from services import EmailHandler
import logging

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s:%(lineno)d'
                           ' - %(message)s', filename='./logs/bot.log',
                    level=logging.INFO)
logger = logging.getLogger(__name__)

ADD_NAME, ADD_PASS, FINISH_ADDING = range(3)


def settings(bot: Bot, update):
    logger.info("received settings command.")

    keyboard = [
        [KeyboardButton("Configure email receiver")],
        [KeyboardButton("Back to menu")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)

    bot.send_message(update.message.chat_id, "Select an option", reply_markup=reply_markup)


def add_new_user(bot, update):
    logger.info("start process of adding user")
    bot.send_message(update.message.chat_id, "enter email")
    return ADD_NAME


def periodic_pulling_mail(bot, job):
    chat_id = str(job.context['chat_id'])
    assert chat_id in EmailHandler.get_users_data()
    user_emails = EmailHandler.get_data_about_user(chat_id)
    for email in user_emails:
        password = user_emails[email]["password"]
        last_uid = user_emails[email]["last_uid"]
        response = EmailHandler.get_new_email(email, password, last_uid)
        if response:
            sender, subject, content = response
            message = f"`New email`\n*To*: {email}\n*Sender*: {sender}\n*Subject*: {subject[:100]}"
            bot.send_message(chat_id, message, parse_mode=ParseMode.MARKDOWN)


def start_email_configure(bot, update):
    logger.info("Configure new email: Step1")
    keyboard = [
        [KeyboardButton("Input new user data")],
        [KeyboardButton("Remove user data")],
        [KeyboardButton("Back to settings")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    bot.send_message(update.message.chat_id, "Select an option",
                     reply_markup=reply_markup)


def start(bot, update):
    keyboard = [
        [KeyboardButton("Menu")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    bot.send_message(update.message.chat_id, "Hello!", reply_markup=reply_markup)


def delete_email(bot, update):
    logger.info("start process of adding user")
    bot.send_message(update.message.chat_id, "enter email")


def add_user_email(bot, update, chat_data):
    logger.info("Configure new email: Step1")
    chat_data['email'] = update.message.text
    domain = chat_data['email'].split("@")[-1]
    if domain not in EmailHandler.get_known_domains():
        bot.send_message(update.message.chat_id, "sorry, this domain is not currently supporting")
        settings(bot, update)
        return ConversationHandler.END
    bot.send_message(update.message.chat_id, "enter password")
    return ADD_PASS


def add_user_password(bot, update, job_queue, chat_data):
    logger.info("Configure new email: Step2")
    password = update.message.text
    if not EmailHandler.add_new_email(update.message.chat_id, chat_data['email'], password):
        bot.send_message(update.message.chat_id, "Cant configure this email")
    else:
        bot.send_message(update.message.chat_id, "Now you will receive notifications when new email will be received")

    job = job_queue.run_repeating(periodic_pulling_mail, 5, context={"chat_id": update.message.chat_id})
    chat_data['job'] = job
    settings(bot, update)
    return ConversationHandler.END


def menu(bot, update):
    keyboard = [
        [KeyboardButton("Settings")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)

    bot.send_message(update.message.chat_id, "Select an option", reply_markup=reply_markup)


with open("token.txt") as token_file:
    TOKEN = token_file.readline()


def main():
    updater = Updater(token=TOKEN)

    for chat_id in EmailHandler.get_users_data():
        updater.job_queue.run_repeating(periodic_pulling_mail, 5, context={"chat_id": chat_id})

    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler("start", start))
    dispatcher.add_handler(RegexHandler("Menu|Back to menu", menu))
    dispatcher.add_handler(RegexHandler("Settings|Back to settings", settings))
    dispatcher.add_handler(RegexHandler("Configure email receiver", start_email_configure))

    adding_new_email_receiver = ConversationHandler(
        entry_points=[RegexHandler("Input new user data", add_new_user)],
        states={
            ADD_NAME: [MessageHandler(Filters.text, add_user_email, pass_chat_data=True)],
            ADD_PASS: [MessageHandler(Filters.text, add_user_password, pass_chat_data=True, pass_job_queue=True)],
        },
        fallbacks=[MessageHandler(Filters.text, settings)]
    )

    dispatcher.add_handler(adding_new_email_receiver)
    updater.start_polling(poll_interval=0.5)


if __name__ == '__main__':
    main()
