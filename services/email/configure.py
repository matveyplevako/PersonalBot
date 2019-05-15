from services.email.functions import *
from telegram.ext import RegexHandler, MessageHandler, Filters, CommandHandler, CallbackQueryHandler


def setup(updater):
    dispatcher = updater.dispatcher

    for user_data in email_utils.get_users_data():
        updater.job_queue.run_repeating(periodic_pulling_mail, 5, context={"chat_id": user_data[0]})

    dispatcher.add_handler(RegexHandler("Configure email receiver", start_email_configure))

    adding_new_email_receiver = ConversationHandler(
        entry_points=[RegexHandler("Input new user data", add_new_user)],
        states={
            ADD_NAME: [MessageHandler(Filters.text, add_user_email, pass_chat_data=True)],
            ADD_PASS: [
                MessageHandler(Filters.text, add_user_password, pass_chat_data=True, pass_job_queue=True)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    deleting_email_receiver = ConversationHandler(
        entry_points=[RegexHandler("Remove email receiver", delete_user_email_select)],
        states={
            DELETE_EMAIL: [MessageHandler(Filters.text, delete_user_email_delete)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    dispatcher.add_handler(deleting_email_receiver)
    dispatcher.add_handler(adding_new_email_receiver)
