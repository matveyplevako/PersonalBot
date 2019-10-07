from services.stoic.functions import *
from telegram.ext import MessageHandler, Filters, CallbackQueryHandler


def setup(updater):
    dispatcher = updater.dispatcher

    for user_data in get_stoic_db().get_all_rows():
        if int(user_data[2]) > 2:
            time = datetime.time(hour=(int(user_data[2]) - 3))
        else:
            time = datetime.time(hour=(24 - int(user_data[2])) % 24)
        updater.job_queue.run_daily(daily_job, time, context={"chat_id": user_data[0]}, name=user_data[0])

    dispatcher.add_handler(MessageHandler(Filters.regex("Daily stoic quote menu"), stoic_menu))
    dispatcher.add_handler(MessageHandler(Filters.regex("Manage subscription"), stoic_subscription_menu))
    dispatcher.add_handler(MessageHandler(Filters.regex("Get quote for today"), get_quote_for_today))
    dispatcher.add_handler(MessageHandler(Filters.regex("Cancel daily subscription"), stop_receiving_quotes))

    adding_new_attendance_record = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("Get quote by day"),
                                     get_data_from_user(
                                         "Send the day [0, 365] you want to get quote for\nor /cancel"))],
        states={
            PROCESS_DATA: [MessageHandler(Filters.text, get_quote_selected_day)],
        },
        fallbacks=[MessageHandler(Filters.all, cancel)]
    )

    set_receiving_hour_conversation = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("Set receiving hour"),
                                     get_data_from_user(
                                         "Send the hour (24h format) you want to receive daily quote at\nor /cancel"))],
        states={
            PROCESS_DATA: [MessageHandler(Filters.text, set_receiving_hour)],
        },
        fallbacks=[MessageHandler(Filters.all, cancel)]
    )

    set_day_conversation = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("Set quotes day"),
                                     get_data_from_user(
                                         "Send the day you from want to receive daily quote\nor /cancel"))],
        states={
            PROCESS_DATA: [MessageHandler(Filters.text, set_day)],
        },
        fallbacks=[MessageHandler(Filters.all, cancel)]
    )

    dispatcher.add_handler(adding_new_attendance_record)
    dispatcher.add_handler(set_receiving_hour_conversation)
    dispatcher.add_handler(set_day_conversation)
    dispatcher.add_handler(CallbackQueryHandler(get_content, pattern="^(ru|eng|img)"))
