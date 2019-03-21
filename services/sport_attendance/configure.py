from telegram.ext import RegexHandler, MessageHandler, Filters, CommandHandler, ConversationHandler
from services.sport_attendance.functions import *


def setup(updater):
    dispatcher = updater.dispatcher

    dispatcher.add_handler(RegexHandler("Sport complex attendance", select_option))

    adding_new_attendance_record = ConversationHandler(
        entry_points=[RegexHandler("Add attendance", add_record)],
        states={
            ADD_START: [MessageHandler(Filters.text, add_start_time, pass_chat_data=True)],
            ADD_FINISH: [MessageHandler(Filters.text, add_finish_time, pass_chat_data=True)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    dispatcher.add_handler(adding_new_attendance_record)
