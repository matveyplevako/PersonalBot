from telegram.ext import RegexHandler, MessageHandler, Filters, CommandHandler
from services.sport_attendance.functions import *


def setup(updater):
    dispatcher = updater.dispatcher

    dispatcher.add_handler(MessageHandler(Filters.regex("Sport complex attendance"), select_option))

    dispatcher.add_handler(
        MessageHandler(Filters.regex("Get my attendance for this term"), get_attendance_for_this_term))

    getting_attendance_for_period = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("Get my attendance for period"), request_period_from_user)],
        states={
            GET_FOR_PERIOD: [MessageHandler(Filters.text, get_attendance_for_period)]
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    adding_new_attendance_record = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("Add attendance"), add_record)],
        states={
            ADD_START: [MessageHandler(Filters.text, add_start_time, pass_chat_data=True)],
            ADD_FINISH: [MessageHandler(Filters.text, add_finish_time, pass_chat_data=True)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    dispatcher.add_handler(getting_attendance_for_period)
    dispatcher.add_handler(adding_new_attendance_record)
