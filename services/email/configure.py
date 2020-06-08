from services.email.functions import *
from telegram.ext import MessageHandler, Filters, CallbackQueryHandler


def setup(updater):
    dispatcher = updater.dispatcher

    updater.job_queue.run_once(periodic_pulling_mail, 5, context={"job_queue": updater.job_queue})

    dispatcher.add_handler(MessageHandler(Filters.regex("Configure email receiver"), start_email_configure))
    dispatcher.add_handler(CallbackQueryHandler(send_doc, pattern="^email:*"))

    adding_new_email_receiver = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("Input new user data"), add_new_user)],
        states={
            ADD_NAME: [MessageHandler(Filters.text, add_user_email, pass_chat_data=True)],
            ADD_PASS: [
                MessageHandler(Filters.text, add_user_password, pass_chat_data=True, pass_job_queue=True)],
        },
        fallbacks=[MessageHandler(Filters.all, cancel)],
        persistent=True, name='adding_new_email_receiver'
    )

    deleting_email_receiver = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("Remove email receiver"), delete_user_email_select)],
        states={
            DELETE_EMAIL: [MessageHandler(Filters.text, delete_user_email_delete)],
        },
        fallbacks=[MessageHandler(Filters.all, cancel)],
        persistent=True, name='deleting_email_receiver'
    )

    dispatcher.add_handler(deleting_email_receiver)
    dispatcher.add_handler(adding_new_email_receiver)
