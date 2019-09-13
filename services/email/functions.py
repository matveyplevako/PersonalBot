from telegram.ext import ConversationHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton, ParseMode
from services.logger import logger
from services.email import email_utils
from services.initial.functions import settings
import traceback

ADD_NAME, ADD_PASS, FINISH_ADDING, DELETE_EMAIL = range(4)


def cancel(update, context):
    bot = context.bot
    logger.error("Cancel the process")
    settings(update, context)
    return ConversationHandler.END


def add_new_user(update, context):
    bot = context.bot
    logger.info("Start process of adding user")
    bot.send_message(update.message.chat_id, "enter email\nor /cancel")
    return ADD_NAME


def delete_user_email_select(update, context):
    bot = context.bot
    logger.info("Start process of deleting user")
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
    logger.info("Handling email to delete")
    email_utils.remove_email_from_user(update.message.chat_id, update.message.text)
    bot.send_message(update.message.chat_id, "deleted")
    settings(update, context)
    return ConversationHandler.END


def periodic_pulling_mail(context):
    bot = context.bot
    job = context.job
    chat_id = str(job.context['chat_id'])
    user_data = email_utils.get_data_about_user(chat_id)
    for data in user_data:
        email = data[1]
        password = data[2]
        last_uid = data[3]
        try:
            response = email_utils.get_new_email(email, password, last_uid, chat_id)
        except EOFError:
            logger.error("EOFError")
            continue
        except Exception as e:
            print(e)
            logger.error("Error while pulling new email")
            logger.error(traceback.print_exc())
            logger.error(email)
            continue
        if response:
            sender, subject, image = response
            logger.info(f"New email to {email} from {sender}")
            sender = sender.replace("_", "\_")
            subject = subject.replace("_", "\_")
            subject = subject.replace("*", "\*")
            email = email.replace("_", "\_")
            if image is None:
                message = f"`New email`\n*To*: {email}\n*Sender*: {sender}\n*Subject*: {subject[:100]}\n"
            else:
                message = f"[​​​​​​​​​​​]({image}) `New email`\n*To*: {email}\n*Sender*: {sender}\n*Subject*: {subject[:100]}\n"

            bot.send_message(chat_id, message, parse_mode=ParseMode.MARKDOWN)


def start_email_configure(update, context):
    bot = context.bot
    logger.info("Configure email receiver command")
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
    logger.info("Configure new email: handling email")
    chat_data['email'] = update.message.text
    domain = chat_data['email'].split("@")[-1]
    email_data = email_utils.get_domain_data(domain)
    if not email_data:
        bot.send_message(update.message.chat_id,
                         "sorry, this domain is not currently supporting, write to @matveyplevako")
        logger.error("Unknown domain")
        return cancel(update, context)
    chat_data['imap'] = email_data[0][1]
    bot.send_message(update.message.chat_id, "enter password")
    return ADD_PASS


def add_user_password(update, context):
    bot = context.bot
    chat_data = context.chat_data
    job_queue = context.job_queue
    logger.info("Configure new email: handling password")
    password = update.message.text
    if not email_utils.add_new_email(update.message.chat_id, chat_data['email'], password, chat_data['imap']):
        bot.send_message(update.message.chat_id, "Password does not match or server does not respond")
        logger.error("Password does not match or server does not respond")
        return cancel(update, context)
    else:
        logger.info("Successful configured new email receiver")
        bot.send_message(update.message.chat_id, "Now you will receive notifications when new email will be received")
        job_queue.run_repeating(periodic_pulling_mail, 10, context={"chat_id": update.message.chat_id})

    settings(update, context)
    return ConversationHandler.END
