from telegram.ext import ConversationHandler, run_async
from telegram import ReplyKeyboardMarkup, KeyboardButton, ParseMode, InlineKeyboardButton, InlineKeyboardMarkup, \
    InputMediaDocument
from services.email import email_utils
from services.initial.functions import settings
import logging
import traceback
import sys
import os
from pymongo import MongoClient
from bson.objectid import ObjectId

ADD_NAME, ADD_PASS, FINISH_ADDING, DELETE_EMAIL = range(4)

LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
logging.basicConfig(level=logging.DEBUG, format=LOG_FORMAT)


def cancel(update, context):
    settings(update, context)
    return ConversationHandler.END


def get_mongo():
    client = MongoClient(os.environ["MONGODB_URI"], retryWrites=False)
    db = client.get_database()
    collection = db.storage
    return collection


def add_new_user(update, context):
    bot = context.bot
    bot.send_message(update.message.chat_id, "enter email\nor /cancel")
    return ADD_NAME


def delete_user_email_select(update, context):
    bot = context.bot
    keyboard = []
    data = email_utils.get_data_about_user(update.message.chat_id)

    for user_data in data:
        keyboard.append([KeyboardButton(user_data[1])])

    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    if not keyboard:
        bot.send_message(update.message.chat_id, "You dont have registered email receivers")
        return cancel(update, context)

    bot.send_message(update.message.chat_id, "Select email\nor /cancel", reply_markup=reply_markup)
    return DELETE_EMAIL


def delete_user_email_delete(update, context):
    bot = context.bot
    email_utils.remove_email_from_user(update.message.chat_id, update.message.text)
    bot.send_message(update.message.chat_id, "deleted")
    settings(update, context)
    return ConversationHandler.END


def single_user_mail(bot, chat_id):
    user_data = email_utils.get_data_about_user(chat_id)
    for data in user_data:
        email = data[1]
        password = data[2]
        last_uid = data[3]
        try:
            response = email_utils.get_new_email(email, password, last_uid, chat_id)
        except Exception as e:
            logging.error(e)
            logging.error(traceback.format_tb(sys.exc_info()[-1]))
            continue

        if response:
            sender, subject, image, prefix = response
            sender = sender.replace("_", "\_")
            subject = subject.replace("_", "\_")
            subject = subject.replace("*", "\*")
            email = email.replace("_", "\_")
            html_template_filename = prefix + ".html"
            if image is None:
                message = f"`New email`\n*To*: {email}\n*Sender*: {sender}\n*Subject*: {subject[:100]}\n"
            else:
                message = f"[​​​​​​​​​​​]({image}) `New email`\n*To*: {email}\n*Sender*: {sender}\n*Subject*: {subject[:100]}\n"

            reply_markup = None
            if html_template_filename:
                with open(html_template_filename, 'rb') as file:
                    document_message = bot.send_document(chat_id, document=file, disable_notification=True,
                                                         filename=sender + ".html")
                    bot.delete_message(chat_id, message_id=document_message.message_id)
                    file_id = document_message.document.file_id

                    collection = get_mongo()
                    key = collection.insert_one({"file_id": file_id, "subject": subject}).inserted_id
                    keyboard = [[InlineKeyboardButton("show email", callback_data=f"email:{key}")]]

                os.remove(html_template_filename)
                reply_markup = InlineKeyboardMarkup(keyboard)

            bot.send_message(chat_id, message, parse_mode=ParseMode.MARKDOWN, reply_markup=reply_markup)


def send_doc(update, context):
    bot = context.bot
    query = update.callback_query
    _, key = query.data.split(":")
    collection = get_mongo()
    file = collection.find_one({"_id": ObjectId(key)})
    file_id = file["file_id"]
    email_subject = file["subject"]
    if file_id:
        bot.send_document(
            chat_id=query.message.chat_id,
            caption=email_subject,
            document=file_id,
        )


@run_async
def periodic_pulling_mail(context):
    for user_data in email_utils.get_users_data():
        try:
            single_user_mail(context.bot, user_data[0])
        except Exception as e:
            logging.error(e)
            logging.error(traceback.format_tb(sys.exc_info()[-1]))

    context.job_queue.run_once(periodic_pulling_mail, 5, context={"job_queue": context.job_queue})


def start_email_configure(update, context):
    bot = context.bot
    keyboard = [
        [KeyboardButton("Input new user data")],
        [KeyboardButton("Remove email receiver")],
        [KeyboardButton("Back to settings")]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard,
                                       one_time_keyboard=True,
                                       resize_keyboard=True)
    bot.send_message(update.message.chat_id, "Select an option",
                     reply_markup=reply_markup)


def add_user_email(update, context):
    bot = context.bot
    chat_data = context.chat_data
    chat_data['email'] = update.message.text
    domain = chat_data['email'].split("@")[-1]
    email_data = email_utils.get_domain_data(domain)
    if not email_data:
        bot.send_message(update.message.chat_id,
                         "sorry, this domain is not currently supporting, write to @matveyplevako")
        return cancel(update, context)
    chat_data['imap'] = email_data[0][1]
    bot.send_message(update.message.chat_id, "enter password")
    return ADD_PASS


def add_user_password(update, context):
    bot = context.bot
    chat_data = context.chat_data
    password = update.message.text
    bot.delete_message(update.message.chat_id, update.message.message_id)
    if not email_utils.add_new_email(update.message.chat_id, chat_data['email'], password, chat_data['imap']):
        bot.send_message(update.message.chat_id, "Password does not match or server does not respond")
        return cancel(update, context)
    else:
        bot.send_message(update.message.chat_id, "Now you will receive notifications when new email will be received")

    settings(update, context)
    return ConversationHandler.END
