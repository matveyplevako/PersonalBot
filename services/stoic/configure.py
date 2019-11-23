from services.stoic.functions import *
from telegram.ext import MessageHandler, Filters, CallbackQueryHandler


def setup(updater):
    dispatcher = updater.dispatcher

    LOGGER.info(get_stoic_db().get_all_rows())
    for user_data in get_stoic_db().get_all_rows():
        hour, minute = map(int, user_data[2].split(":"))
        if hour > 2:
            running_time = datetime.time(hour=(int(hour) - 3), minute=minute)
        else:
            running_time = datetime.time(hour=21 + int(hour), minute=minute)

        updater.job_queue.run_daily(daily_job, time=running_time, context={"chat_id": user_data[0]}, name=user_data[0])

    dispatcher.add_handler(MessageHandler(Filters.regex("Daily stoic quote menu"), stoic_menu))
    dispatcher.add_handler(MessageHandler(Filters.regex("Manage subscription"), stoic_subscription_menu))
    dispatcher.add_handler(MessageHandler(Filters.regex("Get quote for today"), get_quote_for_today))
    dispatcher.add_handler(MessageHandler(Filters.regex("Cancel daily subscription"), stop_receiving_quotes))

    quote_by_day = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("Get quote by day"),
                                     get_data_from_user(
                                         "Send the day [0, 365] you want to get quote for\nor /cancel"))],
        states={
            PROCESS_DATA: [MessageHandler(Filters.text, get_quote_selected_day, pass_job_queue=True)],
        },
        fallbacks=[MessageHandler(Filters.all, cancel)],
        persistent=True, name="quote_by_day"
    )

    set_receiving_hour_conversation = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("Set receiving hour"),
                                     get_data_from_user(
                                         "Send the hour (24h format) and minute you want to receive daily quote at\nor /cancel"))],
        states={
            PROCESS_DATA: [MessageHandler(Filters.text, set_receiving_time, pass_job_queue=True)],
        },
        fallbacks=[MessageHandler(Filters.all, cancel)],
        persistent=True, name="set_receiving_hour_conversation"
    )

    set_day_conversation = ConversationHandler(
        entry_points=[MessageHandler(Filters.regex("Set quotes day"),
                                     get_data_from_user(
                                         "Send the day you from want to receive daily quote\nor /cancel"))],
        states={
            PROCESS_DATA: [MessageHandler(Filters.text, set_day)],
        },
        fallbacks=[MessageHandler(Filters.all, cancel)],
        persistent=True, name="set_day_conversation"
    )

    dispatcher.add_handler(quote_by_day)
    dispatcher.add_handler(set_receiving_hour_conversation)
    dispatcher.add_handler(set_day_conversation)
    dispatcher.add_handler(CallbackQueryHandler(get_content, pattern="^(ru|eng|img)"))
